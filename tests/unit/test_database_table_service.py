import pytest
import uuid
from app.exceptions import EntityNotFoundException
from app.models import DataType
from app.schemas import (
    DatabaseTableCreateSchema,
    DatabaseTableQuerySchema,
    DatabaseTableUpdateSchema,
    TableColumnCreateSchema,
)
from app.services.database_table_service import DatabaseTableService


@pytest.mark.asyncio
async def test_add_database_table(
    database_table_service, sample_database_table_data
):
    """Test adding a new database_table"""
    database_table = await database_table_service.add(sample_database_table_data)

    assert database_table.id is not None
    assert database_table.name == sample_database_table_data.name
    assert database_table.description == sample_database_table_data.description


@pytest.mark.asyncio
async def test_get_database_table(
    database_table_service, sample_database_table_data
):
    """Test retrieving a database_table by ID"""
    created_database_table = await database_table_service.add(
        sample_database_table_data
    )
    retrieved_database_table = await database_table_service.get(
        created_database_table.id
    )

    assert retrieved_database_table is not None
    assert retrieved_database_table.id == created_database_table.id
    assert retrieved_database_table.name == sample_database_table_data.name


@pytest.mark.asyncio
async def test_delete_database_table(
    database_table_service, sample_database_table_data
):
    """Test deleting a database_table"""
    created_database_table = await database_table_service.add(
        sample_database_table_data
    )

    deleted_database_table = await database_table_service.delete(
        created_database_table.id
    )
    assert deleted_database_table.id == created_database_table.id

    with pytest.raises(EntityNotFoundException) as nfe:
        await database_table_service.get(created_database_table.id)
    assert "not found" in str(nfe.value)


@pytest.mark.asyncio
async def test_update_database_table(
    database_table_service, sample_database_table_data
):
    """Test updating a database_table"""
    created_database_table = await database_table_service.add(
        sample_database_table_data
    )

    updated_data = DatabaseTableUpdateSchema(
        name="Updated DatabaseTable",
        deleted=False,
        description="Updated Description",
    )

    updated_database_table = await database_table_service.update(
        created_database_table.id, updated_data
    )

    assert updated_database_table is not None
    assert updated_database_table.id == created_database_table.id
    assert updated_database_table.name == "Updated DatabaseTable"
    assert updated_database_table.description == "Updated Description"


@pytest.mark.asyncio
async def test_find_database_tables(
    database_table_service: DatabaseTableService, sample_database_table_data
):
    """Test finding database_tables with pagination and sorting"""
    # Create multiple database_tables
    database_tables_to_create = [
        DatabaseTableCreateSchema(
            name=f"DatabaseTable {i}",
            description=f"Description {i}",
            deleted=False,
            database_schema_id=uuid.uuid4(),
            database_id=uuid.uuid4(),
            display_name=f"table.test{i}",
            fully_qualified_name=f"test.table{i}",
            updated_by=f"tester{i}",
            columns=[
                TableColumnCreateSchema(
                    name="name",
                    display_name="name",
                    description="column",
                    data_type=DataType.INT,
                ),
            ],
        )
        for i in range(3)
    ]

    for database_table_data in database_tables_to_create:
        await database_table_service.add(database_table_data)

    opts = DatabaseTableQuerySchema(
        sort_by="name",
        sort_order="asc",
        page_size=2,
    )
    found_database_tables = await database_table_service.find(opts)

    assert len(found_database_tables.items) == 2
    (database_table1, database_table2) = found_database_tables.items
    assert (
        database_table1.name is not None
        and database_table2.name is not None
        and database_table1.name < database_table2.name
    )


@pytest.mark.asyncio
async def test_get_nonexistent_database_table(database_table_service):
    """Test retrieving a non-existent database_table"""
    non_existent_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundException) as nfe:
        await database_table_service.get(non_existent_id)
    assert "not found" in str(nfe.value)


@pytest.mark.asyncio
async def test_update_nonexistent_database_table(
    database_table_service, sample_database_table_data
):
    """Test updating a non-existent database_table"""
    non_existent_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundException) as nfe:
        await database_table_service.update(
            non_existent_id, sample_database_table_data
        )
    assert "not found" in str(nfe.value)
