import pytest
import uuid
from app.exceptions import EntityNotFoundException
from app.schemas import (
    DatabaseSchemaCreateSchema,
    DatabaseSchemaQuerySchema,
    DatabaseSchemaUpdateSchema,
)
from app.services.database_schema_service import DatabaseSchemaService


@pytest.mark.asyncio
async def test_add_database_schema(
    database_schema_service, sample_database_schema_data
):
    """Test adding a new database_schema"""
    database_schema = await database_schema_service.add(
        sample_database_schema_data
    )

    assert database_schema.id is not None
    assert database_schema.name == sample_database_schema_data.name
    assert database_schema.description == sample_database_schema_data.description


@pytest.mark.asyncio
async def test_get_database_schema(
    database_schema_service, sample_database_schema_data
):
    """Test retrieving a database_schema by ID"""
    created_database_schema = await database_schema_service.add(
        sample_database_schema_data
    )
    retrieved_database_schema = await database_schema_service.get(
        created_database_schema.id
    )

    assert retrieved_database_schema is not None
    assert retrieved_database_schema.id == created_database_schema.id
    assert retrieved_database_schema.name == sample_database_schema_data.name


@pytest.mark.asyncio
async def test_delete_database_schema(
    database_schema_service, sample_database_schema_data
):
    """Test deleting a database_schema"""
    created_database_schema = await database_schema_service.add(
        sample_database_schema_data
    )

    deleted_database_schema = await database_schema_service.delete(
        created_database_schema.id
    )
    assert deleted_database_schema.id == created_database_schema.id

    with pytest.raises(EntityNotFoundException) as nfe:
        await database_schema_service.get(created_database_schema.id)
    assert "not found" in str(nfe.value)


@pytest.mark.asyncio
async def test_update_database_schema(
    database_schema_service, sample_database_schema_data
):
    """Test updating a database_schema"""
    created_database_schema = await database_schema_service.add(
        sample_database_schema_data
    )

    updated_data = DatabaseSchemaUpdateSchema(
        name="Updated DatabaseSchema",
        deleted=False,
        description="Updated Description",
    )

    updated_database_schema = await database_schema_service.update(
        created_database_schema.id, updated_data
    )

    assert updated_database_schema is not None
    assert updated_database_schema.id == created_database_schema.id
    assert updated_database_schema.name == "Updated DatabaseSchema"
    assert updated_database_schema.description == "Updated Description"


@pytest.mark.asyncio
async def test_find_database_schemas(
    database_schema_service: DatabaseSchemaService, sample_database_schema_data
):
    """Test finding database_schemas with pagination and sorting"""
    # Create multiple database_schemas
    database_schemas_to_create = [
        DatabaseSchemaCreateSchema(
            name=f"DatabaseSchema {i}",
            description=f"Description {i}",
            display_name=f"Schema name {i}",
            fully_qualified_name=f"provider {i}",
            deleted=False,
            database_id=uuid.uuid4(),
            updated_by="tester",
        )
        for i in range(3)
    ]

    for database_schema_data in database_schemas_to_create:
        await database_schema_service.add(database_schema_data)

    opts = DatabaseSchemaQuerySchema(
        sort_by="name",
        sort_order="asc",
        page_size=2,
    )
    found_database_schemas = await database_schema_service.find(opts)

    assert len(found_database_schemas.items) == 2
    (database_schema1, database_schema2) = found_database_schemas.items
    assert (
        database_schema1.name is not None
        and database_schema2.name is not None
        and database_schema1.name < database_schema2.name
    )


@pytest.mark.asyncio
async def test_get_nonexistent_database_schema(database_schema_service):
    """Test retrieving a non-existent database_schema"""
    non_existent_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundException) as nfe:
        await database_schema_service.get(non_existent_id)
    assert "not found" in str(nfe.value)


@pytest.mark.asyncio
async def test_update_nonexistent_database_schema(
    database_schema_service, sample_database_schema_data
):
    """Test updating a non-existent database_schema"""
    non_existent_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundException) as nfe:
        await database_schema_service.update(
            non_existent_id, sample_database_schema_data
        )
    assert "not found" in str(nfe.value)
