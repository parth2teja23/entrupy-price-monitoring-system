import asyncio
import sys
import os

# Add server directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.session import engine
from models.base import Base
from models.product import Product  # Import models to ensure they are registered with Base

async def init_models():
    async with engine.begin() as conn:
        print("Creating database tables...")
        # Optional: uncomment the next line to drop all tables before creating (full reset)
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_models())