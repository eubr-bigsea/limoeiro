import pytest
import pytest_asyncio
import datetime

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ...database import Base
from ...schemas import DomainCreateRequestSchema
from ...services.domain_service import DomainService

# Test database URL for SQLite
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Create a test async engine"""
    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    try:
        yield engine
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine):
    """Create a test async session"""
    async_session = sessionmaker(
        async_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

@pytest_asyncio.fixture
async def domain_service(async_session):
    """Create a DomainService instance"""
    ds = DomainService(async_session)
    return ds

@pytest_asyncio.fixture
def sample_domain_data():
    """Sample domain data for testing"""
    return DomainCreateRequestSchema(
        name="Test Domain",
        display_name="Test Domain",
        fully_qualified_name="Test Domain",
        description="Test Description",
        updated_by="Admin",
        updated_at=datetime.datetime.now(),
    )
