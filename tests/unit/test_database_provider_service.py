import pytest
import uuid
from app.schemas import DatabaseProviderCreateSchema, DatabaseProviderQuerySchema, DatabaseProviderUpdateSchema
from app.services.database_provider_service import DatabaseProviderService

@pytest.mark.asyncio
async def test_add_database_provider(
    database_provider_service, sample_database_provider_data
):
    """Test adding a new database_provider"""
    database_provider = await database_provider_service.add(
        sample_database_provider_data
    )

    assert database_provider.id is not None
    assert database_provider.name == sample_database_provider_data.name
    assert (
        database_provider.description
        == sample_database_provider_data.description
    )


@pytest.mark.asyncio
async def test_get_database_provider(
    database_provider_service, sample_database_provider_data
):
    """Test retrieving a database_provider by ID"""
    created_database_provider = await database_provider_service.add(
        sample_database_provider_data
    )
    retrieved_database_provider = await database_provider_service.get(
        created_database_provider.id
    )

    assert retrieved_database_provider is not None
    assert retrieved_database_provider.id == created_database_provider.id
    assert retrieved_database_provider.name == sample_database_provider_data.name


@pytest.mark.asyncio
async def test_delete_database_provider(
    database_provider_service, sample_database_provider_data
):
    """Test deleting a database_provider"""
    created_database_provider = await database_provider_service.add(
        sample_database_provider_data
    )

    deleted_database_provider = await database_provider_service.delete(
        created_database_provider.id
    )
    assert deleted_database_provider.id == created_database_provider.id

    retrieved_database_provider = await database_provider_service.get(
        created_database_provider.id
    )
    assert retrieved_database_provider is None


@pytest.mark.asyncio
async def test_update_database_provider(
    database_provider_service, sample_database_provider_data
):
    """Test updating a database_provider"""
    created_database_provider = await database_provider_service.add(
        sample_database_provider_data
    )

    updated_data = DatabaseProviderUpdateSchema(
        name="Updated DatabaseProvider",
        deleted=False,
        description="Updated Description",
    )

    updated_database_provider = await database_provider_service.update(
        created_database_provider.id, updated_data
    )

    assert updated_database_provider is not None
    assert updated_database_provider.id == created_database_provider.id
    assert updated_database_provider.name == "Updated DatabaseProvider"
    assert updated_database_provider.description == "Updated Description"


@pytest.mark.asyncio
async def test_find_database_providers(
    database_provider_service: DatabaseProviderService,
    sample_database_provider_data,
):
    """Test finding database_providers with pagination and sorting"""
    # Create multiple database_providers
    database_providers_to_create = [
        DatabaseProviderCreateSchema(
            name=f"DatabaseProvider {i}",
            display_name=f"DatabaseProvider {i}",
            updated_by="tester",
            fully_qualified_name=f"DatabaseProvider {i}",
            description=f"Description {i}",
            deleted=False,
            provider_type_id="postgresql",
        )
        for i in range(3)
    ]

    for database_provider_data in database_providers_to_create:
        await database_provider_service.add(database_provider_data)

    opts = DatabaseProviderQuerySchema(
        sort_by="name",
        sort_order="asc",
        page_size=2,
    )
    found_database_providers = await database_provider_service.find(opts)

    assert len(found_database_providers.items) == 2
    (database_provider1, database_provider2) = found_database_providers.items
    assert database_provider1.name < database_provider2.name


@pytest.mark.asyncio
async def test_get_nonexistent_database_provider(database_provider_service):
    """Test retrieving a non-existent database_provider"""
    non_existent_id = uuid.uuid4()
    database_provider = await database_provider_service.get(non_existent_id)
    assert database_provider is None


@pytest.mark.asyncio
async def test_update_nonexistent_database_provider(
    database_provider_service, sample_database_provider_data
):
    """Test updating a non-existent database_provider"""
    non_existent_id = uuid.uuid4()
    updated_database_provider = await database_provider_service.update(
        non_existent_id, sample_database_provider_data
    )
    assert updated_database_provider is None
