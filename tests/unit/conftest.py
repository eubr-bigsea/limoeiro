import datetime
import uuid

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from alembic.config import Config
from alembic import command
from app.database import Base
from app.schemas import (
    AIModelCreateSchema,
    DatabaseCreateSchema,
    DatabaseProviderConnectionCreateSchema,
    DatabaseProviderCreateSchema,
    DatabaseProviderIngestionCreateSchema,
    DatabaseSchemaCreateSchema,
    DatabaseTableCreateSchema,
    DomainCreateSchema,
    LayerCreateSchema,
    TagCreateSchema,
)
from app.services.a_i_model_service import AIModelService
from app.services.database_provider_connection_service import (
    DatabaseProviderConnectionService,
)
from app.services.database_provider_ingestion_service import (
    DatabaseProviderIngestionService,
)
from app.services.database_provider_service import DatabaseProviderService
from app.services.database_provider_type_service import (
    DatabaseProviderTypeService,
)
from app.services.database_schema_service import DatabaseSchemaService
from app.services.database_service import DatabaseService
from app.services.database_table_service import DatabaseTableService
from app.services.domain_service import DomainService
from app.services.layer_service import LayerService
from app.services.tag_service import TagService

# Test database URL for SQLite
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def anyio_backend():
    """Ensures AnyIO uses asyncio backend for session-scoped fixtures."""
    return "asyncio"



@pytest_asyncio.fixture(scope="session", autouse=True, loop_scope="session")
async def setup_test_db():
    """Recreate the database before tests and apply migrations."""
    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)
    # Run Alembic migrations
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")
    yield  # Run tests

@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def async_engine(setup_test_db):
    """Create a test async engine"""
    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Do not execute! Let it to Alembic
    #async with engine.begin() as conn:
    #    await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        # async with engine.begin() as conn:
        #     await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine):
    """Create a test async session"""
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:  # type: ignore
        try:
            yield session
            await session.rollback() #rollback after each test.
        finally:
            await session.close()


@pytest_asyncio.fixture
async def domain_service(async_session):
    """Create a DomainService instance"""
    ds = DomainService(async_session)
    return ds


@pytest_asyncio.fixture
async def tag_service(async_session):
    return TagService(async_session)


@pytest_asyncio.fixture
async def layer_service(async_session):
    return LayerService(async_session)


@pytest_asyncio.fixture
async def a_i_model_service(async_session):
    return AIModelService(async_session)


@pytest_asyncio.fixture
async def database_provider_connection_service(async_session):
    return DatabaseProviderConnectionService(async_session)


@pytest_asyncio.fixture
async def database_service(async_session):
    return DatabaseService(async_session)


@pytest_asyncio.fixture
async def database_provider_service(async_session):
    return DatabaseProviderService(async_session)


@pytest_asyncio.fixture
async def database_schema_service(async_session):
    return DatabaseSchemaService(async_session)


@pytest_asyncio.fixture
async def database_table_service(async_session):
    return DatabaseTableService(async_session)


@pytest_asyncio.fixture
async def database_provider_type_service(async_session):
    return DatabaseProviderTypeService(async_session)


@pytest_asyncio.fixture
async def database_provider_ingestion_service(async_session):
    return DatabaseProviderIngestionService(async_session)


@pytest_asyncio.fixture
def sample_domain_data():
    """Sample domain data for testing"""
    return DomainCreateSchema(
        name="Test Domain",
        description="Domain",
        deleted=False,
    )


@pytest_asyncio.fixture
def sample_tag_data():
    return TagCreateSchema(
        name="test",
        description="Tag used in tests",
        deleted=False,
        applicable_to="Column",
    )


@pytest_asyncio.fixture
def sample_layer_data():
    return LayerCreateSchema(
        name="raw layer",
        description="Layer used in tests",
        deleted=True,
    )


@pytest_asyncio.fixture
def sample_a_i_model_data():
    return AIModelCreateSchema(
        name="classification model",
        display_name="Name display",
        fully_qualified_name="iris.dataset",
        version="1.0.1",
        updated_at=datetime.datetime.utcnow(),
        updated_by="tester",
        server="http://ia01.uucp",
        source="http://su.uucp",
        description="Layer used in tests",
        deleted=True,
        type="classification",
    )


@pytest_asyncio.fixture
def sample_database_provider_connection_data():
    return DatabaseProviderConnectionCreateSchema(
        user_name="joe",
        password="fool",
        host="server0",
        port=1455,
        database="northwind",
        extra_parameters="{}",
        provider_id="FIXME",
    )


@pytest_asyncio.fixture
def sample_database_data():
    return DatabaseCreateSchema(
        name="classification model",
        display_name="Name display",
        fully_qualified_name="iris.dataset",
        version="1.0.1",
        updated_at=datetime.datetime.utcnow(),
        updated_by="tester",
        description="Database used in tests",
        deleted=True,
        retention_period="1A",
        provider_id=uuid.uuid4(),
    )


@pytest_asyncio.fixture
def sample_database_provider_data():
    return DatabaseProviderCreateSchema(
        name="raw layer",
        description="Layer used in tests",
        deleted=True,
        provider_type_id="mariadb",
        fully_qualified_name="provider",
        display_name="Provider name",
        updated_by="tester",
    )


@pytest_asyncio.fixture
def sample_database_schema_data():
    return DatabaseSchemaCreateSchema(
        name="raw layer",
        description="Layer used in tests",
        deleted=True,
        fully_qualified_name="provider",
        display_name="Schema name",
        updated_by="tester",
        database_id=uuid.uuid4(),
    )


@pytest_asyncio.fixture
def sample_database_table_data():
    return DatabaseTableCreateSchema(
        name="raw layer",
        description="Layer used in tests",
        deleted=True,
        fully_qualified_name="provider",
        display_name="Schema name",
        updated_by="tester",
        database_schema_id=uuid.uuid4(),
        database_id=uuid.uuid4(),
        columns=[],
    )


@pytest_asyncio.fixture
def sample_database_provider_type_data():
    return None


@pytest_asyncio.fixture
def sample_database_provider_ingestion_data():
    return DatabaseProviderIngestionCreateSchema(
        name="raw layer",
        provider_id=uuid.uuid4(),
        deleted=True,
        type="ingestion",
    )
