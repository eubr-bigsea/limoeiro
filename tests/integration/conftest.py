# Setup test client with mocked dependencies
import uuid
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.routers import (
    database_provider_router,
    database_provider_type_router,
    database_provider_ingestion_router,
    database_provider_connection_router,
    database_router,
    database_table_router,
    domain_router,
    database_schema_router,
    a_i_model_router,
    layer_router,
    tag_router,
)
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
from app.services.database_service import DatabaseService
from app.services.domain_service import DomainService
from app.services.a_i_model_service import AIModelService
from app.services.layer_service import LayerService
from app.services.tag_service import TagService


@pytest.fixture
def mock_tag_service():
    (mocked, original_dependency, get_service_ref) = mock_service(
        TagService, tag_router
    )
    yield mocked
    restore_mock(original_dependency, get_service_ref)


@pytest.fixture
def mock_layer_service():
    (mocked, original_dependency, get_service_ref) = mock_service(
        LayerService, layer_router
    )
    yield mocked
    restore_mock(original_dependency, get_service_ref)


@pytest.fixture
def mock_a_i_model_service():
    (mocked, original_dependency, get_service_ref) = mock_service(
        AIModelService, a_i_model_router
    )
    yield mocked
    restore_mock(original_dependency, get_service_ref)


@pytest.fixture
def mock_database_provider_type_service():
    (mocked, original_dependency, get_service_ref) = mock_service(
        DatabaseProviderTypeService, database_provider_type_router
    )
    yield mocked
    restore_mock(original_dependency, get_service_ref)


@pytest.fixture
def mock_database_provider_service():
    (mocked, original_dependency, get_service_ref) = mock_service(
        DatabaseProviderService, database_provider_router
    )
    yield mocked
    restore_mock(original_dependency, get_service_ref)


@pytest.fixture
def mock_database_provider_connection_service():
    (mocked, original_dependency, get_service_ref) = mock_service(
        DatabaseProviderConnectionService, database_provider_connection_router
    )
    yield mocked
    restore_mock(original_dependency, get_service_ref)


@pytest.fixture
def mock_database_provider_ingestion_service():
    (mocked, original_dependency, get_service_ref) = mock_service(
        DatabaseProviderIngestionService, database_provider_ingestion_router
    )
    yield mocked
    restore_mock(original_dependency, get_service_ref)


@pytest.fixture
def mock_database_service():
    (mocked, original_dependency, get_service_ref) = mock_service(
        DatabaseService, database_router
    )
    yield mocked
    restore_mock(original_dependency, get_service_ref)


@pytest.fixture
def mock_database_schema_service():
    (mocked, original_dependency, get_service_ref) = mock_service(
        DatabaseService, database_schema_router
    )
    yield mocked
    restore_mock(original_dependency, get_service_ref)


@pytest.fixture
def mock_database_table_service():
    (mocked, original_dependency, get_service_ref) = mock_service(
        DatabaseService, database_table_router
    )
    yield mocked
    restore_mock(original_dependency, get_service_ref)


@pytest.fixture
def mock_domain_service():
    (mocked, original_dependency, get_service_ref) = mock_service(
        DomainService, domain_router
    )
    yield mocked
    restore_mock(original_dependency, get_service_ref)


def restore_mock(original_dependency, get_service_ref):
    # Restore the original dependency or clear the override
    if original_dependency:
        app.dependency_overrides[get_service_ref] = original_dependency
    else:
        app.dependency_overrides.pop(get_service_ref, None)


def mock_service(spec, router):
    mock_service = AsyncMock(spec=spec)

    get_service_ref = router._get_service
    # Store the original dependency
    original_dependency = app.dependency_overrides.get(get_service_ref)

    # Override the dependency
    app.dependency_overrides[get_service_ref] = lambda: mock_service

    return mock_service, original_dependency, get_service_ref


@pytest.fixture
def test_uuid():
    """Generate a UUID for testing."""
    return uuid.uuid4()


@pytest.fixture
async def async_client():
    """Create an AsyncClient for testing FastAPI routes."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        yield client
