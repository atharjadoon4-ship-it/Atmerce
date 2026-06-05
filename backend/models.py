from sqlalchemy import Column, String, Float, Integer, Boolean, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from database import Base
import uuid
from datetime import datetime, timezone

def generate_uuid():
    return str(uuid.uuid4())

def get_current_timestamp():
    return datetime.now(timezone.utc).isoformat()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default='customer', index=True)
    wishlist = Column(JSON, default=list)
    created_at = Column(String(50), default=get_current_timestamp)
    
    orders = relationship('Order', back_populates='user', cascade='all, delete-orphan')
    reviews = relationship('Review', back_populates='user', cascade='all, delete-orphan')

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    image = Column(Text)
    parent_id = Column(String(36), ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    active = Column(Boolean, default=True, index=True)
    created_at = Column(String(50), default=get_current_timestamp)
    
    products = relationship('Product', back_populates='category')
    parent = relationship('Category', remote_side=[id])

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, nullable=True)
    images = Column(JSON, default=list)
    category_id = Column(String(36), ForeignKey('categories.id', ondelete='CASCADE'), nullable=False, index=True)
    stock = Column(Integer, default=0)
    active = Column(Boolean, default=True, index=True)
    ratings_avg = Column(Float, default=0.0)
    ratings_count = Column(Integer, default=0)
    specifications = Column(JSON, default=dict)
    created_at = Column(String(50), default=get_current_timestamp, index=True)
    
    category = relationship('Category', back_populates='products')
    reviews = relationship('Review', back_populates='product', cascade='all, delete-orphan')

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    items = Column(JSON, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String(50), default='pending', index=True)
    shipping_address = Column(JSON, nullable=False)
    coupon_code = Column(String(50), nullable=True)
    created_at = Column(String(50), default=get_current_timestamp, index=True)
    
    user = relationship('User', back_populates='orders')

class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user_name = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False)
    approved = Column(Boolean, default=False, index=True)
    created_at = Column(String(50), default=get_current_timestamp, index=True)
    
    product = relationship('Product', back_populates='reviews')
    user = relationship('User', back_populates='reviews')

class Coupon(Base):
    __tablename__ = 'coupons'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(50), unique=True, nullable=False, index=True)
    discount_type = Column(String(20), nullable=False)
    discount_value = Column(Float, nullable=False)
    min_purchase = Column(Float, default=0)
    max_uses = Column(Integer, default=0)
    uses_count = Column(Integer, default=0)
    expires_at = Column(String(50), nullable=True)
    active = Column(Boolean, default=True, index=True)

class Banner(Base):
    __tablename__ = 'banners'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    image = Column(Text, nullable=False)
    link = Column(Text, nullable=True)
    position = Column(Integer, default=0, index=True)
    active = Column(Boolean, default=True, index=True)

class Settings(Base):
    __tablename__ = 'settings'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    logo = Column(Text)
    footer_text = Column(Text)
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    seo_title = Column(String(255))
    seo_description = Column(Text)

class FileMetadata(Base):
    __tablename__ = 'files'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    storage_path = Column(String(500), nullable=False, unique=True, index=True)
    original_filename = Column(String(255))
    content_type = Column(String(100))
    size = Column(Integer)
    is_deleted = Column(Boolean, default=False, index=True)
    created_at = Column(String(50), default=get_current_timestamp)