from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form, Query, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import base64
from storage import init_storage, put_object, get_object
from email_service import send_email, get_order_confirmation_email, get_order_status_email

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 720

# Models
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

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({'id': payload['user_id']}, {'_id': 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def require_admin(user = Depends(get_current_user)):
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# Auth routes
@api_router.post("/auth/register")
async def register(data: UserRegister):
    existing = await db.users.find_one({'email': data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user_doc = {
        'id': user_id,
        'email': data.email,
        'password': hash_password(data.password),
        'name': data.name,
        'role': 'customer',
        'wishlist': [],
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user_doc)
    
    token = create_token(user_id, data.email, 'customer')
    return {'token': token, 'user': {'id': user_id, 'email': data.email, 'name': data.name, 'role': 'customer'}}

@api_router.post("/auth/login")
async def login(data: UserLogin):
    user = await db.users.find_one({'email': data.email}, {'_id': 0})
    if not user or not verify_password(data.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user['id'], user['email'], user['role'])
    return {'token': token, 'user': {'id': user['id'], 'email': user['email'], 'name': user['name'], 'role': user['role']}}

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(user = Depends(get_current_user)):
    return UserResponse(**user)

# Categories
@api_router.post("/categories", response_model=CategoryResponse)
async def create_category(data: CategoryCreate, admin = Depends(require_admin)):
    category_id = str(uuid.uuid4())
    doc = data.model_dump()
    doc['id'] = category_id
    doc['created_at'] = datetime.now(timezone.utc).isoformat()
    await db.categories.insert_one(doc)
    return CategoryResponse(**doc)

@api_router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(active_only: bool = False):
    query = {'active': True} if active_only else {}
    categories = await db.categories.find(query, {'_id': 0}).to_list(1000)
    return [CategoryResponse(**cat) for cat in categories]

@api_router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str):
    category = await db.categories.find_one({'id': category_id}, {'_id': 0})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryResponse(**category)

@api_router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: str, data: CategoryCreate, admin = Depends(require_admin)):
    result = await db.categories.update_one(
        {'id': category_id},
        {'$set': data.model_dump()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    updated = await db.categories.find_one({'id': category_id}, {'_id': 0})
    return CategoryResponse(**updated)

@api_router.delete("/categories/{category_id}")
async def delete_category(category_id: str, admin = Depends(require_admin)):
    result = await db.categories.delete_one({'id': category_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {'message': 'Category deleted'}

# Products
@api_router.post("/products", response_model=ProductResponse)
async def create_product(data: ProductCreate, admin = Depends(require_admin)):
    product_id = str(uuid.uuid4())
    doc = data.model_dump()
    doc['id'] = product_id
    doc['ratings_avg'] = 0
    doc['ratings_count'] = 0
    doc['created_at'] = datetime.now(timezone.utc).isoformat()
    await db.products.insert_one(doc)
    return ProductResponse(**doc)

@api_router.get("/products", response_model=List[ProductResponse])
async def get_products(
    category_id: Optional[str] = None, 
    search: Optional[str] = None, 
    active_only: bool = True,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    query = {}
    if active_only:
        query['active'] = True
    if category_id:
        query['category_id'] = category_id
    if search:
        query['$or'] = [{'name': {'$regex': search, '$options': 'i'}}, {'description': {'$regex': search, '$options': 'i'}}]
    
    skip = (page - 1) * limit
    products = await db.products.find(query, {'_id': 0}).sort('created_at', -1).skip(skip).limit(limit).to_list(limit)
    return [ProductResponse(**prod) for prod in products]

@api_router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    product = await db.products.find_one({'id': product_id}, {'_id': 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse(**product)

@api_router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, data: ProductCreate, admin = Depends(require_admin)):
    result = await db.products.update_one(
        {'id': product_id},
        {'$set': data.model_dump()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    updated = await db.products.find_one({'id': product_id}, {'_id': 0})
    return ProductResponse(**updated)

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str, admin = Depends(require_admin)):
    result = await db.products.delete_one({'id': product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {'message': 'Product deleted'}


# Product Recommendations
@api_router.get("/products/{product_id}/recommendations", response_model=List[ProductResponse])
async def get_product_recommendations(product_id: str, limit: int = Query(4, ge=1, le=20)):
    """Get product recommendations (simple: same category + popular)"""
    product = await db.products.find_one({'id': product_id}, {'_id': 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get products from same category, sorted by ratings
    recommendations = await db.products.find(
        {
            'category_id': product['category_id'],
            'id': {'$ne': product_id},
            'active': True
        },
        {'_id': 0}
    ).sort([('ratings_avg', -1), ('ratings_count', -1)]).limit(limit).to_list(limit)
    
    return [ProductResponse(**prod) for prod in recommendations]

@api_router.get("/recommendations/popular", response_model=List[ProductResponse])
async def get_popular_products(limit: int = Query(8, ge=1, le=20)):
    """Get popular products based on ratings and order frequency"""
    # Get products with highest ratings
    products = await db.products.find(
        {'active': True, 'ratings_count': {'$gt': 0}},
        {'_id': 0}
    ).sort([('ratings_avg', -1), ('ratings_count', -1)]).limit(limit).to_list(limit)
    
    return [ProductResponse(**prod) for prod in products]

@api_router.get("/recommendations/personalized", response_model=List[ProductResponse])
async def get_personalized_recommendations(user = Depends(get_current_user), limit: int = Query(8, ge=1, le=20)):
    """Get personalized recommendations based on user's order history"""
    # Get user's past orders
    user_orders = await db.orders.find({'user_id': user['id']}, {'_id': 0}).to_list(100)
    
    if not user_orders:
        # Fallback to popular products if no order history
        return await get_popular_products(limit)
    
    # Extract categories from ordered products
    ordered_product_ids = set()
    category_frequency = {}
    
    for order in user_orders:
        for item in order.get('items', []):
            ordered_product_ids.add(item.get('product_id'))
    
    # Get categories from ordered products
    ordered_products = await db.products.find(
        {'id': {'$in': list(ordered_product_ids)}},
        {'_id': 0, 'category_id': 1}
    ).to_list(1000)
    
    for prod in ordered_products:
        cat_id = prod.get('category_id')
        category_frequency[cat_id] = category_frequency.get(cat_id, 0) + 1
    
    # Get top categories
    top_categories = sorted(category_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
    top_category_ids = [cat[0] for cat in top_categories]
    
    # Recommend products from favorite categories that user hasn't ordered
    recommendations = await db.products.find(
        {
            'category_id': {'$in': top_category_ids},
            'id': {'$nin': list(ordered_product_ids)},
            'active': True
        },
        {'_id': 0}
    ).sort([('ratings_avg', -1), ('ratings_count', -1)]).limit(limit).to_list(limit)
    
    return [ProductResponse(**prod) for prod in recommendations]

# Reviews
@api_router.post("/reviews", response_model=ReviewResponse)
async def create_review(data: ReviewCreate, user = Depends(get_current_user)):
    review_id = str(uuid.uuid4())
    doc = data.model_dump()
    doc['id'] = review_id
    doc['user_id'] = user['id']
    doc['user_name'] = user['name']
    doc['approved'] = False
    doc['created_at'] = datetime.now(timezone.utc).isoformat()
    await db.reviews.insert_one(doc)
    return ReviewResponse(**doc)

@api_router.get("/reviews", response_model=List[ReviewResponse])
async def get_reviews(
    product_id: Optional[str] = None, 
    approved_only: bool = True,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    query = {}
    if approved_only:
        query['approved'] = True
    if product_id:
        query['product_id'] = product_id
    
    skip = (page - 1) * limit
    reviews = await db.reviews.find(query, {'_id': 0}).sort('created_at', -1).skip(skip).limit(limit).to_list(limit)
    return [ReviewResponse(**rev) for rev in reviews]

@api_router.put("/reviews/{review_id}/approve")
async def approve_review(review_id: str, admin = Depends(require_admin)):
    result = await db.reviews.update_one({'id': review_id}, {'$set': {'approved': True}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    
    review = await db.reviews.find_one({'id': review_id}, {'_id': 0})
    product_id = review['product_id']
    
    pipeline = [
        {'$match': {'product_id': product_id, 'approved': True}},
        {'$group': {'_id': None, 'avg_rating': {'$avg': '$rating'}, 'count': {'$sum': 1}}}
    ]
    result = await db.reviews.aggregate(pipeline).to_list(1)
    
    if result:
        await db.products.update_one(
            {'id': product_id},
            {'$set': {'ratings_avg': round(result[0]['avg_rating'], 1), 'ratings_count': result[0]['count']}}
        )
    
    return {'message': 'Review approved'}

@api_router.delete("/reviews/{review_id}")
async def delete_review(review_id: str, admin = Depends(require_admin)):
    result = await db.reviews.delete_one({'id': review_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    return {'message': 'Review deleted'}

# Orders
@api_router.post("/orders", response_model=OrderResponse)
async def create_order(data: OrderCreate, user = Depends(get_current_user)):
    order_id = str(uuid.uuid4())
    doc = data.model_dump()
    doc['id'] = order_id
    doc['user_id'] = user['id']
    doc['status'] = 'pending'
    doc['created_at'] = datetime.now(timezone.utc).isoformat()
    
    if data.coupon_code:
        coupon = await db.coupons.find_one({'code': data.coupon_code, 'active': True}, {'_id': 0})
        if coupon:
            await db.coupons.update_one({'id': coupon['id']}, {'$inc': {'uses_count': 1}})
    
    await db.orders.insert_one(doc)
    
    # Send order confirmation email
    try:
        html = get_order_confirmation_email(
            order_id=order_id,
            customer_name=user['name'],
            total=data.total,
            items=data.items
        )
        await send_email(
            to_email=user['email'],
            subject=f"Order Confirmation - #{order_id[:8]}",
            html_content=html
        )
    except Exception as e:
        logger.error(f"Failed to send order confirmation email: {e}")
    
    return OrderResponse(**doc)

@api_router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    user = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    query = {'user_id': user['id']} if user['role'] != 'admin' else {}
    skip = (page - 1) * limit
    orders = await db.orders.find(query, {'_id': 0}).sort('created_at', -1).skip(skip).limit(limit).to_list(limit)
    return [OrderResponse(**order) for order in orders]

@api_router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, user = Depends(get_current_user)):
    order = await db.orders.find_one({'id': order_id}, {'_id': 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if user['role'] != 'admin' and order['user_id'] != user['id']:
        raise HTTPException(status_code=403, detail="Access denied")
    return OrderResponse(**order)

@api_router.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, status: str, admin = Depends(require_admin)):
    result = await db.orders.update_one({'id': order_id}, {'$set': {'status': status}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Send status update email
    try:
        order = await db.orders.find_one({'id': order_id}, {'_id': 0})
        user = await db.users.find_one({'id': order['user_id']}, {'_id': 0})
        
        if user and status in ['processing', 'shipped', 'delivered']:
            html = get_order_status_email(
                order_id=order_id,
                customer_name=user['name'],
                status=status
            )
            await send_email(
                to_email=user['email'],
                subject=f"Order Update - #{order_id[:8]}",
                html_content=html
            )
    except Exception as e:
        logger.error(f"Failed to send order status email: {e}")
    
    return {'message': 'Order status updated'}

# Coupons
@api_router.post("/coupons", response_model=CouponResponse)
async def create_coupon(data: CouponCreate, admin = Depends(require_admin)):
    coupon_id = str(uuid.uuid4())
    doc = data.model_dump()
    doc['id'] = coupon_id
    doc['uses_count'] = 0
    doc['active'] = True
    await db.coupons.insert_one(doc)
    return CouponResponse(**doc)

@api_router.get("/coupons", response_model=List[CouponResponse])
async def get_coupons(admin = Depends(require_admin)):
    coupons = await db.coupons.find({}, {'_id': 0}).to_list(1000)
    return [CouponResponse(**c) for c in coupons]

@api_router.get("/coupons/validate/{code}")
async def validate_coupon(code: str, total: float):
    coupon = await db.coupons.find_one({'code': code, 'active': True}, {'_id': 0})
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    if coupon['min_purchase'] > total:
        raise HTTPException(status_code=400, detail=f"Minimum purchase of {coupon['min_purchase']} required")
    if coupon['max_uses'] > 0 and coupon['uses_count'] >= coupon['max_uses']:
        raise HTTPException(status_code=400, detail="Coupon usage limit reached")
    
    discount = 0
    if coupon['discount_type'] == 'percentage':
        discount = (total * coupon['discount_value']) / 100
    else:
        discount = coupon['discount_value']
    
    return {'valid': True, 'discount': discount, 'final_total': max(0, total - discount)}

@api_router.delete("/coupons/{coupon_id}")
async def delete_coupon(coupon_id: str, admin = Depends(require_admin)):
    result = await db.coupons.delete_one({'id': coupon_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return {'message': 'Coupon deleted'}

# Banners
@api_router.post("/banners", response_model=BannerResponse)
async def create_banner(data: BannerCreate, admin = Depends(require_admin)):
    banner_id = str(uuid.uuid4())
    doc = data.model_dump()
    doc['id'] = banner_id
    await db.banners.insert_one(doc)
    return BannerResponse(**doc)

@api_router.get("/banners", response_model=List[BannerResponse])
async def get_banners(active_only: bool = True):
    query = {'active': True} if active_only else {}
    banners = await db.banners.find(query, {'_id': 0}).sort('position', 1).to_list(100)
    return [BannerResponse(**b) for b in banners]

@api_router.delete("/banners/{banner_id}")
async def delete_banner(banner_id: str, admin = Depends(require_admin)):
    result = await db.banners.delete_one({'id': banner_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Banner not found")
    return {'message': 'Banner deleted'}

# Settings
@api_router.get("/settings")
async def get_settings():
    settings = await db.settings.find_one({}, {'_id': 0})
    if not settings:
        default_settings = {
            'id': str(uuid.uuid4()),
            'logo': '',
            'footer_text': '© 2026 E-Shop. All rights reserved.',
            'contact_email': 'support@eshop.com',
            'contact_phone': '+1-234-567-8900',
            'seo_title': 'E-Shop - Your Online Shopping Destination',
            'seo_description': 'Shop the latest products at great prices'
        }
        await db.settings.insert_one(default_settings)
        return default_settings
    return settings

@api_router.put("/settings")
async def update_settings(data: SettingsUpdate, admin = Depends(require_admin)):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    await db.settings.update_one({}, {'$set': update_data}, upsert=True)
    return await get_settings()

# Wishlist
@api_router.post("/wishlist/{product_id}")
async def add_to_wishlist(product_id: str, user = Depends(get_current_user)):
    await db.users.update_one(
        {'id': user['id']},
        {'$addToSet': {'wishlist': product_id}}
    )
    return {'message': 'Added to wishlist'}

@api_router.delete("/wishlist/{product_id}")
async def remove_from_wishlist(product_id: str, user = Depends(get_current_user)):
    await db.users.update_one(
        {'id': user['id']},
        {'$pull': {'wishlist': product_id}}
    )
    return {'message': 'Removed from wishlist'}

@api_router.get("/wishlist", response_model=List[ProductResponse])
async def get_wishlist(user = Depends(get_current_user)):
    user_data = await db.users.find_one({'id': user['id']}, {'_id': 0})
    if not user_data or not user_data.get('wishlist'):
        return []
    
    products = await db.products.find({'id': {'$in': user_data['wishlist']}}, {'_id': 0}).to_list(1000)
    return [ProductResponse(**p) for p in products]

# Admin stats
@api_router.get("/admin/stats")
async def get_admin_stats(admin = Depends(require_admin)):
    total_products = await db.products.count_documents({})
    total_orders = await db.orders.count_documents({})
    total_customers = await db.users.count_documents({'role': 'customer'})
    
    pipeline = [
        {'$group': {'_id': None, 'total_revenue': {'$sum': '$total'}}}
    ]
    revenue_result = await db.orders.aggregate(pipeline).to_list(1)
    total_revenue = revenue_result[0]['total_revenue'] if revenue_result else 0
    
    recent_orders = await db.orders.find({}, {'_id': 0}).sort('created_at', -1).limit(10).to_list(10)
    
    return {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders
    }

# Image upload with Object Storage
@api_router.post("/upload")
async def upload_image(file: UploadFile = File(...), admin = Depends(require_admin)):
    try:
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif']
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type. Only images allowed.")
        
        # Validate file size (max 5MB)
        contents = await file.read()
        if len(contents) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Max 5MB allowed.")
        
        # Generate unique filename
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        filename = f"{uuid.uuid4()}.{ext}"
        storage_path = f"eshop/images/{filename}"
        
        # Upload to object storage
        result = put_object(storage_path, contents, file.content_type)
        
        # Store file metadata in database
        file_doc = {
            'id': str(uuid.uuid4()),
            'storage_path': result['path'],
            'original_filename': file.filename,
            'content_type': file.content_type,
            'size': result.get('size', len(contents)),
            'is_deleted': False,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await db.files.insert_one(file_doc)
        
        # Return URL that points to our download endpoint
        return {
            'url': f"/api/files/{result['path']}",
            'file_id': file_doc['id'],
            'size': file_doc['size']
        }
    except Exception as e:
        logger.error(f"Image upload failed: {e}")
        # Fallback to base64 if storage fails
        base64_encoded = base64.b64encode(contents).decode('utf-8')
        return {'url': f"data:{file.content_type};base64,{base64_encoded}", 'fallback': True}

# Download file from object storage
@api_router.get("/files/{path:path}")
async def download_file(path: str):
    # Check if file exists in database
    file_record = await db.files.find_one({'storage_path': path, 'is_deleted': False}, {'_id': 0})
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        data, content_type = get_object(path)
        return Response(
            content=data,
            media_type=file_record.get('content_type', content_type),
            headers={
                'Cache-Control': 'public, max-age=31536000',
                'Content-Disposition': f'inline; filename="{file_record.get("original_filename", "image.jpg")}"'
            }
        )
    except Exception as e:
        logger.error(f"File download failed: {e}")
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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

@app.on_event("startup")
async def create_admin_user():
    # Initialize object storage
    try:
        init_storage()
        logger.info("Object storage initialized")
    except Exception as e:
        logger.warning(f"Storage initialization failed: {e}")
    
    # Create default admin user
    admin = await db.users.find_one({'email': 'admin@eshop.com'})
    if not admin:
        admin_doc = {
            'id': str(uuid.uuid4()),
            'email': 'admin@eshop.com',
            'password': hash_password('admin123'),
            'name': 'Admin',
            'role': 'admin',
            'wishlist': [],
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(admin_doc)
        logger.info('Admin user created: admin@eshop.com / admin123')