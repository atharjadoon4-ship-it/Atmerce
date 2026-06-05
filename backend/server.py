from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Query, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, update as sql_update, delete as sql_delete
from sqlalchemy.orm import selectinload
import os
import logging
from pathlib import Path
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt

from database import get_db
from models import User, Category, Product, Order, Review, Coupon, Banner, Settings, FileMetadata
from storage import init_storage, put_object, get_object
from email_service import send_email, get_order_confirmation_email, get_order_status_email

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 720

# Pydantic Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    wishlist: List[str] = []

class CategoryCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    image: Optional[str] = None
    parent_id: Optional[str] = None
    active: bool = True

class CategoryResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    image: Optional[str] = None
    parent_id: Optional[str] = None
    active: bool
    created_at: str

class ProductCreate(BaseModel):
    name: str
    slug: str
    description: str
    price: float
    discount_price: Optional[float] = None
    images: List[str] = []
    category_id: str
    stock: int = 0
    active: bool = True
    specifications: Dict[str, Any] = {}

class ProductResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    price: float
    discount_price: Optional[float] = None
    images: List[str]
    category_id: str
    stock: int
    active: bool
    ratings_avg: float
    ratings_count: int
    specifications: Dict[str, Any]
    created_at: str

class ReviewCreate(BaseModel):
    product_id: str
    rating: int
    comment: str

class ReviewResponse(BaseModel):
    id: str
    product_id: str
    user_id: str
    user_name: str
    rating: int
    comment: str
    approved: bool
    created_at: str

class OrderCreate(BaseModel):
    items: List[Dict[str, Any]]
    total: float
    shipping_address: Dict[str, str]
    coupon_code: Optional[str] = None

class OrderResponse(BaseModel):
    id: str
    user_id: str
    items: List[Dict[str, Any]]
    total: float
    status: str
    shipping_address: Dict[str, str]
    created_at: str

class CouponCreate(BaseModel):
    code: str
    discount_type: str
    discount_value: float
    min_purchase: float = 0
    max_uses: int = 0
    expires_at: Optional[str] = None

class CouponResponse(BaseModel):
    id: str
    code: str
    discount_type: str
    discount_value: float
    min_purchase: float
    max_uses: int
    uses_count: int
    expires_at: Optional[str]
    active: bool

class BannerCreate(BaseModel):
    title: str
    image: str
    link: Optional[str] = None
    position: int = 0
    active: bool = True

class BannerResponse(BaseModel):
    id: str
    title: str
    image: str
    link: Optional[str]
    position: int
    active: bool

class SettingsUpdate(BaseModel):
    logo: Optional[str] = None
    footer_text: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None

# Auth utilities
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str, email: str, role: str) -> str:
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        result = await db.execute(select(User).where(User.id == payload['user_id']))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def require_admin(user: User = Depends(get_current_user)):
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# Auth routes
@api_router.post("/auth/register")
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        id=str(uuid.uuid4()),
        email=data.email,
        password=hash_password(data.password),
        name=data.name,
        role='customer',
        wishlist=[],
        created_at=datetime.now(timezone.utc).isoformat()
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    token = create_token(user.id, user.email, user.role)
    return {'token': token, 'user': {'id': user.id, 'email': user.email, 'name': user.name, 'role': user.role}}

@api_router.post("/auth/login")
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user.id, user.email, user.role)
    return {'token': token, 'user': {'id': user.id, 'email': user.email, 'name': user.name, 'role': user.role}}

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        wishlist=user.wishlist or []
    )

# Categories
@api_router.post("/categories", response_model=CategoryResponse)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    category = Category(id=str(uuid.uuid4()), **data.model_dump(), created_at=datetime.now(timezone.utc).isoformat())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return CategoryResponse(**category.__dict__)

@api_router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(active_only: bool = False, db: AsyncSession = Depends(get_db)):
    query = select(Category)
    if active_only:
        query = query.where(Category.active == True)
    result = await db.execute(query)
    categories = result.scalars().all()
    return [CategoryResponse(**cat.__dict__) for cat in categories]

@api_router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryResponse(**category.__dict__)

@api_router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: str, data: CategoryCreate, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    for key, value in data.model_dump().items():
        setattr(category, key, value)
    await db.commit()
    await db.refresh(category)
    return CategoryResponse(**category.__dict__)

@api_router.delete("/categories/{category_id}")
async def delete_category(category_id: str, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(category)
    await db.commit()
    return {'message': 'Category deleted'}

# Products
@api_router.post("/products", response_model=ProductResponse)
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    product = Product(
        id=str(uuid.uuid4()),
        **data.model_dump(),
        ratings_avg=0,
        ratings_count=0,
        created_at=datetime.now(timezone.utc).isoformat()
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return ProductResponse(**product.__dict__)

@api_router.get("/products", response_model=List[ProductResponse])
async def get_products(
    category_id: Optional[str] = None,
    search: Optional[str] = None,
    active_only: bool = True,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(Product)
    if active_only:
        query = query.where(Product.active == True)
    if category_id:
        query = query.where(Product.category_id == category_id)
    if search:
        query = query.where(or_(
            Product.name.ilike(f'%{search}%'),
            Product.description.ilike(f'%{search}%')
        ))
    
    query = query.order_by(Product.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()
    return [ProductResponse(**prod.__dict__) for prod in products]

@api_router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse(**product.__dict__)

@api_router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, data: ProductCreate, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in data.model_dump().items():
        setattr(product, key, value)
    await db.commit()
    await db.refresh(product)
    return ProductResponse(**product.__dict__)

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.delete(product)
    await db.commit()
    return {'message': 'Product deleted'}

# Product Recommendations
@api_router.get("/products/{product_id}/recommendations", response_model=List[ProductResponse])
async def get_product_recommendations(product_id: str, limit: int = Query(4, ge=1, le=20), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    query = select(Product).where(
        and_(
            Product.category_id == product.category_id,
            Product.id != product_id,
            Product.active == True
        )
    ).order_by(Product.ratings_avg.desc(), Product.ratings_count.desc()).limit(limit)
    
    result = await db.execute(query)
    recommendations = result.scalars().all()
    return [ProductResponse(**prod.__dict__) for prod in recommendations]

@api_router.get("/recommendations/popular", response_model=List[ProductResponse])
async def get_popular_products(limit: int = Query(8, ge=1, le=20), db: AsyncSession = Depends(get_db)):
    query = select(Product).where(
        and_(Product.active == True, Product.ratings_count > 0)
    ).order_by(Product.ratings_avg.desc(), Product.ratings_count.desc()).limit(limit)
    
    result = await db.execute(query)
    products = result.scalars().all()
    return [ProductResponse(**prod.__dict__) for prod in products]

@api_router.get("/recommendations/personalized", response_model=List[ProductResponse])
async def get_personalized_recommendations(user: User = Depends(get_current_user), limit: int = Query(8, ge=1, le=20), db: AsyncSession = Depends(get_db)):
    # Get user's past orders
    result = await db.execute(select(Order).where(Order.user_id == user.id))
    user_orders = result.scalars().all()
    
    if not user_orders:
        return await get_popular_products(limit, db)
    
    # Extract ordered product IDs
    ordered_product_ids = set()
    for order in user_orders:
        for item in order.items:
            ordered_product_ids.add(item.get('product_id'))
    
    # Get categories from ordered products
    result = await db.execute(
        select(Product.category_id, func.count(Product.id).label('count'))
        .where(Product.id.in_(list(ordered_product_ids)))
        .group_by(Product.category_id)
        .order_by(func.count(Product.id).desc())
        .limit(3)
    )
    top_categories = [row[0] for row in result.all()]
    
    # Recommend products from favorite categories
    query = select(Product).where(
        and_(
            Product.category_id.in_(top_categories),
            Product.id.notin_(list(ordered_product_ids)),
            Product.active == True
        )
    ).order_by(Product.ratings_avg.desc(), Product.ratings_count.desc()).limit(limit)
    
    result = await db.execute(query)
    recommendations = result.scalars().all()
    return [ProductResponse(**prod.__dict__) for prod in recommendations]

# Continue in next message due to length...

# Reviews
@api_router.post("/reviews", response_model=ReviewResponse)
async def create_review(data: ReviewCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    review = Review(
        id=str(uuid.uuid4()),
        user_id=user.id,
        user_name=user.name,
        approved=False,
        created_at=datetime.now(timezone.utc).isoformat(),
        **data.model_dump()
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return ReviewResponse(**review.__dict__)

@api_router.get("/reviews", response_model=List[ReviewResponse])
async def get_reviews(
    product_id: Optional[str] = None,
    approved_only: bool = True,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(Review)
    if approved_only:
        query = query.where(Review.approved == True)
    if product_id:
        query = query.where(Review.product_id == product_id)
    
    query = query.order_by(Review.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    reviews = result.scalars().all()
    return [ReviewResponse(**rev.__dict__) for rev in reviews]

@api_router.put("/reviews/{review_id}/approve")
async def approve_review(review_id: str, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    review.approved = True
    await db.commit()
    
    # Update product ratings
    result = await db.execute(
        select(func.avg(Review.rating), func.count(Review.id))
        .where(and_(Review.product_id == review.product_id, Review.approved == True))
    )
    avg_rating, count = result.one()
    
    await db.execute(
        sql_update(Product)
        .where(Product.id == review.product_id)
        .values(ratings_avg=round(float(avg_rating), 1) if avg_rating else 0, ratings_count=count)
    )
    await db.commit()
    
    return {'message': 'Review approved'}

@api_router.delete("/reviews/{review_id}")
async def delete_review(review_id: str, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    await db.delete(review)
    await db.commit()
    return {'message': 'Review deleted'}

# Orders
@api_router.post("/orders", response_model=OrderResponse)
async def create_order(data: OrderCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    order = Order(
        id=str(uuid.uuid4()),
        user_id=user.id,
        status='pending',
        created_at=datetime.now(timezone.utc).isoformat(),
        **data.model_dump()
    )
    
    if data.coupon_code:
        result = await db.execute(select(Coupon).where(and_(Coupon.code == data.coupon_code, Coupon.active == True)))
        coupon = result.scalar_one_or_none()
        if coupon:
            coupon.uses_count += 1
    
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    # Send order confirmation email
    try:
        html = get_order_confirmation_email(
            order_id=order.id,
            customer_name=user.name,
            total=data.total,
            items=data.items
        )
        await send_email(
            to_email=user.email,
            subject=f"Order Confirmation - #{order.id[:8]}",
            html_content=html
        )
    except Exception as e:
        logging.error(f"Failed to send order confirmation email: {e}")
    
    return OrderResponse(**order.__dict__)

@api_router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(Order)
    if user.role != 'admin':
        query = query.where(Order.user_id == user.id)
    
    query = query.order_by(Order.created_at.desc()).offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    orders = result.scalars().all()
    return [OrderResponse(**order.__dict__) for order in orders]

@api_router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if user.role != 'admin' and order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return OrderResponse(**order.__dict__)

@api_router.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, status: str, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    await db.commit()
    
    # Send status update email
    try:
        user_result = await db.execute(select(User).where(User.id == order.user_id))
        user_obj = user_result.scalar_one_or_none()
        
        if user_obj and status in ['processing', 'shipped', 'delivered']:
            html = get_order_status_email(
                order_id=order_id,
                customer_name=user_obj.name,
                status=status
            )
            await send_email(
                to_email=user_obj.email,
                subject=f"Order Update - #{order_id[:8]}",
                html_content=html
            )
    except Exception as e:
        logging.error(f"Failed to send order status email: {e}")
    
    return {'message': 'Order status updated'}

# Coupons
@api_router.post("/coupons", response_model=CouponResponse)
async def create_coupon(data: CouponCreate, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    coupon = Coupon(id=str(uuid.uuid4()), uses_count=0, active=True, **data.model_dump())
    db.add(coupon)
    await db.commit()
    await db.refresh(coupon)
    return CouponResponse(**coupon.__dict__)

@api_router.get("/coupons", response_model=List[CouponResponse])
async def get_coupons(db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(select(Coupon))
    coupons = result.scalars().all()
    return [CouponResponse(**c.__dict__) for c in coupons]

@api_router.get("/coupons/validate/{code}")
async def validate_coupon(code: str, total: float, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Coupon).where(and_(Coupon.code == code, Coupon.active == True)))
    coupon = result.scalar_one_or_none()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    if coupon.min_purchase > total:
        raise HTTPException(status_code=400, detail=f"Minimum purchase of {coupon.min_purchase} required")
    if coupon.max_uses > 0 and coupon.uses_count >= coupon.max_uses:
        raise HTTPException(status_code=400, detail="Coupon usage limit reached")
    
    discount = 0
    if coupon.discount_type == 'percentage':
        discount = (total * coupon.discount_value) / 100
    else:
        discount = coupon.discount_value
    
    return {'valid': True, 'discount': discount, 'final_total': max(0, total - discount)}

@api_router.delete("/coupons/{coupon_id}")
async def delete_coupon(coupon_id: str, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
    coupon = result.scalar_one_or_none()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    await db.delete(coupon)
    await db.commit()
    return {'message': 'Coupon deleted'}

# Banners
@api_router.post("/banners", response_model=BannerResponse)
async def create_banner(data: BannerCreate, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    banner = Banner(id=str(uuid.uuid4()), **data.model_dump())
    db.add(banner)
    await db.commit()
    await db.refresh(banner)
    return BannerResponse(**banner.__dict__)

@api_router.get("/banners", response_model=List[BannerResponse])
async def get_banners(active_only: bool = True, db: AsyncSession = Depends(get_db)):
    query = select(Banner)
    if active_only:
        query = query.where(Banner.active == True)
    query = query.order_by(Banner.position)
    result = await db.execute(query)
    banners = result.scalars().all()
    return [BannerResponse(**b.__dict__) for b in banners]

@api_router.delete("/banners/{banner_id}")
async def delete_banner(banner_id: str, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(select(Banner).where(Banner.id == banner_id))
    banner = result.scalar_one_or_none()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    await db.delete(banner)
    await db.commit()
    return {'message': 'Banner deleted'}

# Settings
@api_router.get("/settings")
async def get_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Settings))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = Settings(
            id=str(uuid.uuid4()),
            logo='',
            footer_text='\u00a9 2026 E-Shop. All rights reserved.',
            contact_email='support@eshop.com',
            contact_phone='+1-234-567-8900',
            seo_title='E-Shop - Your Online Shopping Destination',
            seo_description='Shop the latest products at great prices'
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings.__dict__

@api_router.put("/settings")
async def update_settings(data: SettingsUpdate, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(select(Settings))
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings = Settings(id=str(uuid.uuid4()))
        db.add(settings)
    
    for key, value in data.model_dump().items():
        if value is not None:
            setattr(settings, key, value)
    
    await db.commit()
    await db.refresh(settings)
    return settings.__dict__

# Wishlist
@api_router.post("/wishlist/{product_id}")
async def add_to_wishlist(product_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if product_id not in (user.wishlist or []):
        user.wishlist = (user.wishlist or []) + [product_id]
        await db.commit()
    return {'message': 'Added to wishlist'}

@api_router.delete("/wishlist/{product_id}")
async def remove_from_wishlist(product_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if product_id in (user.wishlist or []):
        user.wishlist = [pid for pid in user.wishlist if pid != product_id]
        await db.commit()
    return {'message': 'Removed from wishlist'}

@api_router.get("/wishlist", response_model=List[ProductResponse])
async def get_wishlist(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not user.wishlist:
        return []
    
    result = await db.execute(select(Product).where(Product.id.in_(user.wishlist)))
    products = result.scalars().all()
    return [ProductResponse(**p.__dict__) for p in products]

# Admin stats
@api_router.get("/admin/stats")
async def get_admin_stats(db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    total_products = await db.scalar(select(func.count(Product.id)))
    total_orders = await db.scalar(select(func.count(Order.id)))
    total_customers = await db.scalar(select(func.count(User.id)).where(User.role == 'customer'))
    total_revenue = await db.scalar(select(func.sum(Order.total))) or 0
    
    result = await db.execute(select(Order).order_by(Order.created_at.desc()).limit(10))
    recent_orders = result.scalars().all()
    
    return {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_revenue': float(total_revenue),
        'recent_orders': [OrderResponse(**o.__dict__).model_dump() for o in recent_orders]
    }

# Image upload
@api_router.post("/upload")
async def upload_image(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    import base64
    try:
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif']
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        contents = await file.read()
        if len(contents) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Max 5MB")
        
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        filename = f"{uuid.uuid4()}.{ext}"
        storage_path = f"eshop/images/{filename}"
        
        result = put_object(storage_path, contents, file.content_type)
        
        file_metadata = FileMetadata(
            id=str(uuid.uuid4()),
            storage_path=result['path'],
            original_filename=file.filename,
            content_type=file.content_type,
            size=result.get('size', len(contents)),
            is_deleted=False,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        db.add(file_metadata)
        await db.commit()
        
        return {
            'url': f"/api/files/{result['path']}",
            'file_id': file_metadata.id,
            'size': file_metadata.size
        }
    except Exception as e:
        logging.error(f"Image upload failed: {e}")
        base64_encoded = base64.b64encode(contents).decode('utf-8')
        return {'url': f"data:{file.content_type};base64,{base64_encoded}", 'fallback': True}

@api_router.get("/files/{path:path}")
async def download_file(path: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FileMetadata).where(and_(FileMetadata.storage_path == path, FileMetadata.is_deleted == False)))
    file_record = result.scalar_one_or_none()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        data, content_type = get_object(path)
        return Response(
            content=data,
            media_type=file_record.content_type or content_type,
            headers={
                'Cache-Control': 'public, max-age=31536000',
                'Content-Disposition': f'inline; filename="{file_record.original_filename or "image.jpg"}"'
            }
        )
    except Exception as e:
        logging.error(f"File download failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to download file")

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    # Initialize object storage
    try:
        init_storage()
        logger.info("Object storage initialized")
    except Exception as e:
        logger.warning(f"Storage initialization failed: {e}")
    
    logger.info("Supabase PostgreSQL connected successfully")
