from __future__ import annotations
from __future__ import annotations
import asyncio
import sys
import os

# Add server directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.session import engine
from models import Base  # This implicitly pulls all imported models due to our __init__.py

async def init_models():
    async with engine.begin() as conn:
        print("Dropping old database tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Creating exact 6-table schema required by Assignment...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully!")
        
    # Inject default API key so Testing / Postman isn't completely locked out instantly
    from sqlalchemy.ext.asyncio import AsyncSession
    from models.security import ApiKey
    import hashlib
    
    async with AsyncSession(engine) as session:
        hashed = hashlib.sha256(b"secret-entrupy-key").hexdigest()
        session.add(ApiKey(key_hash=hashed, name="Default Test Key"))
        await session.commit()
        print("Injected default development api key!")

if __name__ == "__main__":
    asyncio.run(init_models())