import os
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from typing import AsyncGenerator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define the SQLite database URL
# DATABASE_URL = "sqlite:///./test.db"  # This will create a file named 'test.db' in the current directory
DATABASE_URL = os.environ["DB_URL"]

# Create the engine
engine = create_async_engine(
    DATABASE_URL, echo=True, pool_size=10, max_overflow=20
)

# Create a configured "Session" class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create a base class for models
Base = declarative_base()

# Create a session factory
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
