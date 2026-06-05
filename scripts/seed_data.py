#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.insert(0, '/app/backend')
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import uuid
from datetime import datetime, timezone

load_dotenv(Path('/app/backend/.env'))

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

async def seed_data():
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Create categories
    categories = [
        {
            'id': str(uuid.uuid4()),
            'name': 'Electronics',
            'slug': 'electronics',
            'description': 'Latest gadgets and electronics',
            'image': 'https://images.unsplash.com/photo-1498049794561-7780e7231661?crop=entropy&cs=srgb&fm=jpg&q=85',
            'active': True,
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Fashion',
            'slug': 'fashion',
            'description': 'Trending fashion and apparel',
            'image': 'https://images.unsplash.com/photo-1445205170230-053b83016050?crop=entropy&cs=srgb&fm=jpg&q=85',
            'active': True,
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Home & Living',
            'slug': 'home-living',
            'description': 'Furniture and home decor',
            'image': 'https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?crop=entropy&cs=srgb&fm=jpg&q=85',
            'active': True,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.categories.delete_many({})
    await db.categories.insert_many(categories)
    print(f"✓ Created {len(categories)} categories")
    
    # Create products
    products = [
        {
            'id': str(uuid.uuid4()),
            'name': 'Wireless Headphones',
            'slug': 'wireless-headphones',
            'description': 'Premium noise-cancelling wireless headphones with 30-hour battery life',
            'price': 299.99,
            'discount_price': 249.99,
            'images': ['https://images.unsplash.com/photo-1505740420928-5e560c06d30e?crop=entropy&cs=srgb&fm=jpg&q=85'],
            'category_id': categories[0]['id'],
            'stock': 50,
            'active': True,
            'ratings_avg': 4.5,
            'ratings_count': 128,
            'specifications': {'Battery Life': '30 hours', 'Bluetooth': '5.0', 'Weight': '250g'},
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Smart Watch',
            'slug': 'smart-watch',
            'description': 'Fitness tracking smartwatch with heart rate monitor',
            'price': 199.99,
            'discount_price': None,
            'images': ['https://images.unsplash.com/photo-1523275335684-37898b6baf30?crop=entropy&cs=srgb&fm=jpg&q=85'],
            'category_id': categories[0]['id'],
            'stock': 75,
            'active': True,
            'ratings_avg': 4.7,
            'ratings_count': 94,
            'specifications': {'Display': 'AMOLED', 'Water Resistant': 'IP68', 'Battery': '5 days'},
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Laptop Backpack',
            'slug': 'laptop-backpack',
            'description': 'Durable laptop backpack with USB charging port',
            'price': 49.99,
            'discount_price': 39.99,
            'images': ['https://images.unsplash.com/photo-1553062407-98eeb64c6a62?crop=entropy&cs=srgb&fm=jpg&q=85'],
            'category_id': categories[1]['id'],
            'stock': 100,
            'active': True,
            'ratings_avg': 4.3,
            'ratings_count': 56,
            'specifications': {'Capacity': '20L', 'Laptop Size': 'Up to 15.6"', 'Material': 'Polyester'},
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Modern Desk Lamp',
            'slug': 'modern-desk-lamp',
            'description': 'LED desk lamp with adjustable brightness and color temperature',
            'price': 89.99,
            'discount_price': None,
            'images': ['https://images.unsplash.com/photo-1507473885765-e6ed057f782c?crop=entropy&cs=srgb&fm=jpg&q=85'],
            'category_id': categories[2]['id'],
            'stock': 30,
            'active': True,
            'ratings_avg': 4.6,
            'ratings_count': 42,
            'specifications': {'Power': '12W LED', 'Color Temp': '3000K-6500K', 'Brightness': 'Adjustable'},
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Premium Coffee Maker',
            'slug': 'premium-coffee-maker',
            'description': 'Programmable coffee maker with thermal carafe',
            'price': 129.99,
            'discount_price': 99.99,
            'images': ['https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?crop=entropy&cs=srgb&fm=jpg&q=85'],
            'category_id': categories[2]['id'],
            'stock': 25,
            'active': True,
            'ratings_avg': 4.4,
            'ratings_count': 78,
            'specifications': {'Capacity': '12 cups', 'Timer': '24-hour programmable', 'Carafe': 'Thermal'},
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Wireless Mouse',
            'slug': 'wireless-mouse',
            'description': 'Ergonomic wireless mouse with precision tracking',
            'price': 29.99,
            'discount_price': 24.99,
            'images': ['https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?crop=entropy&cs=srgb&fm=jpg&q=85'],
            'category_id': categories[0]['id'],
            'stock': 150,
            'active': True,
            'ratings_avg': 4.2,
            'ratings_count': 210,
            'specifications': {'DPI': '1600', 'Battery': '6 months', 'Connection': 'Wireless 2.4GHz'},
            'created_at': datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.products.delete_many({})
    await db.products.insert_many(products)
    print(f"✓ Created {len(products)} products")
    
    print("\n✓ Seed data created successfully!")
    client.close()

if __name__ == '__main__':
    asyncio.run(seed_data())
