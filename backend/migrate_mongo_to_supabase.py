#!/usr/bin/env python3
"""
Migrate data from MongoDB to Supabase PostgreSQL
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal, engine
from models import User, Category, Product, Order, Review, Coupon, Banner, Settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(Path(__file__).parent / '.env')

# MongoDB connection
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

async def migrate_data():
    # Connect to MongoDB
    mongo_client = AsyncIOMotorClient(MONGO_URL)
    mongo_db = mongo_client[DB_NAME]
    
    # Connect to Supabase
    async with AsyncSessionLocal() as session:
        try:
            # Migrate Users
            logger.info("Migrating users...")
            users = await mongo_db.users.find({}, {'_id': 0}).to_list(10000)
            for user_doc in users:
                user = User(**user_doc)
                session.add(user)
            await session.commit()
            logger.info(f"Migrated {len(users)} users")
            
            # Migrate Categories
            logger.info("Migrating categories...")
            categories = await mongo_db.categories.find({}, {'_id': 0}).to_list(10000)
            for cat_doc in categories:
                category = Category(**cat_doc)
                session.add(category)
            await session.commit()
            logger.info(f"Migrated {len(categories)} categories")
            
            # Migrate Products
            logger.info("Migrating products...")
            products = await mongo_db.products.find({}, {'_id': 0}).to_list(10000)
            for prod_doc in products:
                product = Product(**prod_doc)
                session.add(product)
            await session.commit()
            logger.info(f"Migrated {len(products)} products")
            
            # Migrate Orders
            logger.info("Migrating orders...")
            orders = await mongo_db.orders.find({}, {'_id': 0}).to_list(10000)
            for order_doc in orders:
                order = Order(**order_doc)
                session.add(order)
            await session.commit()
            logger.info(f"Migrated {len(orders)} orders")
            
            # Migrate Reviews
            logger.info("Migrating reviews...")
            reviews = await mongo_db.reviews.find({}, {'_id': 0}).to_list(10000)
            for review_doc in reviews:
                review = Review(**review_doc)
                session.add(review)
            await session.commit()
            logger.info(f"Migrated {len(reviews)} reviews")
            
            # Migrate Coupons
            logger.info("Migrating coupons...")
            coupons = await mongo_db.coupons.find({}, {'_id': 0}).to_list(10000)
            for coupon_doc in coupons:
                coupon = Coupon(**coupon_doc)
                session.add(coupon)
            await session.commit()
            logger.info(f"Migrated {len(coupons)} coupons")
            
            # Migrate Banners
            logger.info("Migrating banners...")
            banners = await mongo_db.banners.find({}, {'_id': 0}).to_list(10000)
            for banner_doc in banners:
                banner = Banner(**banner_doc)
                session.add(banner)
            await session.commit()
            logger.info(f"Migrated {len(banners)} banners")
            
            # Migrate Settings
            logger.info("Migrating settings...")
            settings = await mongo_db.settings.find_one({}, {'_id': 0})
            if settings:
                setting = Settings(**settings)
                session.add(setting)
                await session.commit()
                logger.info("Migrated settings")
            
            logger.info("✓ Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            await session.rollback()
            raise
        finally:
            mongo_client.close()

if __name__ == '__main__':
    asyncio.run(migrate_data())
