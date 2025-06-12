import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.sql.schema import DEFAULT_NAMING_CONVENTION
from contextlib import asynccontextmanager

# Load environment variables from .env file
load_dotenv()

# Define the SQLite database URL
# DATABASE_URL = "sqlite:///./test.db"  # This will create a file named 'test.db' in the current directory
DATABASE_URL = os.environ["DB_URL"]

metadata = MetaData(naming_convention=DEFAULT_NAMING_CONVENTION)
# Create a base class for models
class Base(AsyncAttrs, DeclarativeBase):
    metadata = metadata

if 'sqlite' in DATABASE_URL:
    DATABASE_URL = "sqlite+asyncsqlite:///./test.db"

# Create the engine
engine = create_async_engine(
    DATABASE_URL, echo=True, pool_size=10, max_overflow=20
)

# Create a configured "Session" class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine, # type: ignore
    class_=AsyncSession,
    expire_on_commit=False,
) # type: ignore


# Create a session factory
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False # type: ignore
) # type: ignore

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session: # type: ignore
        yield session
