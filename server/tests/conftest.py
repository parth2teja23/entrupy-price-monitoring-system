from __future__ import annotations
from __future__ import annotations
import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from db.session import get_db
from models.base import Base

# Test database URL (using SQLite memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""      
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_database():
    # Create the test database and tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Insert mock API key
    import hashlib
    from models.security import ApiKey
    async with TestingSessionLocal() as session:
        session.add(ApiKey(
            name="Test Client",
            key_hash=hashlib.sha256("test-secret-key".encode()).hexdigest()
        ))
        await session.commit()

    yield
    # Drop the test database and tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="module")
async def async_client():
    headers = {"X-API-Key": "test-secret-key"}
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=headers)
    yield client
    await client.aclose()
