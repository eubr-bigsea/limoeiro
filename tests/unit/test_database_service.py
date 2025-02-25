import pytest
import uuid
from app.schemas import DatabaseCreateSchema, DatabaseQuerySchema, DatabaseUpdateSchema
from app.services.database_service import DatabaseService

@pytest.mark.asyncio
async def test_add_database(database_service, sample_database_data):
    """Test adding a new database"""
    database = await database_service.add(sample_database_data)

    assert database.id is not None
    assert database.name == sample_database_data.name
    assert database.description == sample_database_data.description


@pytest.mark.asyncio
async def test_get_database(database_service, sample_database_data):
    """Test retrieving a database by ID"""
    created_database = await database_service.add(sample_database_data)
    retrieved_database = await database_service.get(created_database.id)

    assert retrieved_database is not None
    assert retrieved_database.id == created_database.id
    assert retrieved_database.name == sample_database_data.name


@pytest.mark.asyncio
async def test_delete_database(database_service, sample_database_data):
    """Test deleting a database"""
    created_database = await database_service.add(sample_database_data)

    deleted_database = await database_service.delete(created_database.id)
    assert deleted_database.id == created_database.id

    retrieved_database = await database_service.get(created_database.id)
    assert retrieved_database is None


@pytest.mark.asyncio
async def test_update_database(database_service, sample_database_data):
    """Test updating a database"""
    created_database = await database_service.add(sample_database_data)

    updated_data = DatabaseUpdateSchema(
        name="Updated Database", deleted=False, description="Updated Description"
    )

    updated_database = await database_service.update(
        created_database.id, updated_data
    )

    assert updated_database is not None
    assert updated_database.id == created_database.id
    assert updated_database.name == "Updated Database"
    assert updated_database.description == "Updated Description"


@pytest.mark.asyncio
async def test_find_databases(
    database_service: DatabaseService, sample_database_data
):
    """Test finding databases with pagination and sorting"""
    # Create multiple databases
    databases_to_create = [
        DatabaseCreateSchema(
            name=f"Database {i}",
            fully_qualified_name=f"Database {i}",
            display_name=f"Database {i}",
            description=f"Description {i}",
            deleted=False,
            provider_id=uuid.uuid4(),
            updated_by="tester",
        )
        for i in range(3)
    ]

    for database_data in databases_to_create:
        await database_service.add(database_data)

    opts = DatabaseQuerySchema(
        sort_by="name",
        sort_order="asc",
        page_size=2,
    )
    found_databases = await database_service.find(opts)

    assert len(found_databases.items) == 2
    (database1, database2) = found_databases.items
    assert database1.name < database2.name


@pytest.mark.asyncio
async def test_get_nonexistent_database(database_service):
    """Test retrieving a non-existent database"""
    non_existent_id = uuid.uuid4()
    database = await database_service.get(non_existent_id)
    assert database is None


@pytest.mark.asyncio
async def test_update_nonexistent_database(
    database_service, sample_database_data
):
    """Test updating a non-existent database"""
    non_existent_id = uuid.uuid4()
    updated_database = await database_service.update(
        non_existent_id, sample_database_data
    )
    assert updated_database is None
