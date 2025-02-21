import datetime
import uuid
import pytest_asyncio

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.services.database_provider_connection_service import DatabaseProviderConnectionService
from app.services.database_provider_ingestion_service import DatabaseProviderIngestionService
from app.services.database_provider_service import DatabaseProviderService
from app.services.database_provider_type_service import DatabaseProviderTypeService
from app.services.database_schema_service import DatabaseSchemaService
from app.services.database_service import DatabaseService
from app.services.database_table_service import DatabaseTableService
from app.services.i_a_model_service import IAModelService
from app.services.layer_service import LayerService
from app.services.tag_service import TagService

from app.database import Base
from app.schemas import DatabaseCreateSchema, DatabaseProviderConnectionCreateSchema, DatabaseProviderCreateSchema, DatabaseProviderIngestionCreateSchema, DatabaseSchemaCreateSchema, DatabaseTableCreateSchema, DomainCreateSchema, IAModelCreateSchema, LayerCreateSchema, TagCreateSchema
from app.services.domain_service import DomainService

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
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session: # type: ignore
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
async def tag_service(async_session):
    return TagService(async_session)

@pytest_asyncio.fixture
async def layer_service(async_session):
    return LayerService(async_session)

@pytest_asyncio.fixture
async def i_a_model_service(async_session):
    return IAModelService(async_session)

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
        applicable_to="Column"
    )

@pytest_asyncio.fixture
def sample_layer_data():
    return LayerCreateSchema(
        name="raw layer",
        description="Layer used in tests",
        deleted=True,

    )

@pytest_asyncio.fixture
def sample_i_a_model_data():
    return IAModelCreateSchema(
        name="classification model",
        display_name="Name display",
        fully_qualified_name="iris.dataset",
        version="1.0.1",
        updated_at=datetime.datetime.utcnow(),
        updated_by="tester",
        href="fixme",
        owner="tester",
        algorithm="Naive bayes",
        technology="Spark",
        server="ia01",
        source="su",
        description="Layer used in tests",
        deleted=True,

    )
@pytest_asyncio.fixture
def sample_database_provider_connection_data():
    return DatabaseProviderConnectionCreateSchema(
        user_name="joe",
        password="fool",
        host="server0",
        port=1455,
        database="northwind",
        extra_parameters="{}"
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
        href="fixme",
        owner="tester",
        description="Database used in tests",
        deleted=True,
        retention_period="1A",
        provider_id=uuid.uuid4()
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
        owner="sa",
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
        owner="sa",
        database_id=uuid.uuid4()
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
        owner="sa",
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
        type="ingestion"
    )
