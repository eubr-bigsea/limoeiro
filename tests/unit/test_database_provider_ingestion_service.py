import pytest
import uuid
from app.exceptions import EntityNotFoundException
from app.schemas import (
    DatabaseProviderIngestionCreateSchema,
    DatabaseProviderIngestionQuerySchema,
    DatabaseProviderIngestionUpdateSchema,
)
from app.services.database_provider_ingestion_service import (
    DatabaseProviderIngestionService,
)


@pytest.mark.asyncio
async def test_add_database_provider_ingestion(
    database_provider_ingestion_service,
    database_provider_service,
    sample_database_provider_ingestion_data,
):
    """Test adding a new database_provider_ingestion"""
    database_provider = await database_provider_service.add(
        sample_database_provider_ingestion_data[1]
    )

    sample_database_provider_ingestion_data[0].provider_id = database_provider.id
    database_provider_ingestion = await database_provider_ingestion_service.add(
        sample_database_provider_ingestion_data[0]
    )

    assert database_provider_ingestion.id is not None
    assert (
        database_provider_ingestion.name
        == sample_database_provider_ingestion_data[0].name
    )
    assert (
        database_provider_ingestion.exclude_schema
        == sample_database_provider_ingestion_data[0].exclude_schema
    )
    assert (
        database_provider_ingestion.include_schema
        == sample_database_provider_ingestion_data[0].include_schema
    )


@pytest.mark.asyncio
async def test_get_database_provider_ingestion(
    database_provider_ingestion_service,
    database_provider_service,
    sample_database_provider_ingestion_data,
):
    """Test retrieving a database_provider_ingestion by ID"""
    database_provider = await database_provider_service.add(
        sample_database_provider_ingestion_data[1]
    )

    sample_database_provider_ingestion_data[0].provider_id = database_provider.id
    created_database_provider_ingestion = (
        await database_provider_ingestion_service.add(
            sample_database_provider_ingestion_data[0]
        )
    )
    retrieved_database_provider_ingestion = (
        await database_provider_ingestion_service.get(
            created_database_provider_ingestion.id
        )
    )

    assert retrieved_database_provider_ingestion is not None
    assert (
        retrieved_database_provider_ingestion.id
        == created_database_provider_ingestion.id
    )
    assert (
        retrieved_database_provider_ingestion.type
        == sample_database_provider_ingestion_data[0].type
    )


@pytest.mark.asyncio
async def test_delete_database_provider_ingestion(
    database_provider_ingestion_service,
    database_provider_service,
    sample_database_provider_ingestion_data,
):
    """Test deleting a database_provider_ingestion"""
    database_provider = await database_provider_service.add(
        sample_database_provider_ingestion_data[1]
    )

    sample_database_provider_ingestion_data[0].provider_id = database_provider.id

    created_database_provider_ingestion = (
        await database_provider_ingestion_service.add(
            sample_database_provider_ingestion_data[0]
        )
    )

    deleted_database_provider_ingestion = (
        await database_provider_ingestion_service.delete(
            created_database_provider_ingestion.id
        )
    )
    assert (
        deleted_database_provider_ingestion.id
        == created_database_provider_ingestion.id
    )
    with pytest.raises(EntityNotFoundException) as nfe:
        (
            await database_provider_ingestion_service.get(
                created_database_provider_ingestion.id
            )
        )
    assert "not found" in str(nfe.value)


@pytest.mark.asyncio
async def test_update_database_provider_ingestion(
    database_provider_ingestion_service,
    database_provider_service,
    sample_database_provider_ingestion_data,
):
    """Test updating a database_provider_ingestion"""

    database_provider = await database_provider_service.add(
        sample_database_provider_ingestion_data[1]
    )

    sample_database_provider_ingestion_data[0].provider_id = database_provider.id
    created_database_provider_ingestion = (
        await database_provider_ingestion_service.add(
            sample_database_provider_ingestion_data[0]
        )
    )

    updated_data = DatabaseProviderIngestionUpdateSchema(
        name="Ingestion 01",
        provider_id=database_provider.id,
        deleted=False,
        type="ingestion",
        include_database=".+",
        exclude_table="^tmp.+",
    )

    updated_database_provider_ingestion = (
        await database_provider_ingestion_service.update(
            created_database_provider_ingestion.id, updated_data
        )
    )

    assert updated_database_provider_ingestion is not None
    assert (
        updated_database_provider_ingestion.id
        == created_database_provider_ingestion.id
    )
    assert (
        updated_database_provider_ingestion.include_database
        == updated_data.include_database
    )
    assert (
        updated_database_provider_ingestion.exclude_table
        == updated_data.exclude_table
    )


@pytest.mark.asyncio
async def test_find_database_provider_ingestions(
    database_provider_ingestion_service: DatabaseProviderIngestionService,
    database_provider_service: DatabaseProviderIngestionService,
    sample_database_provider_ingestion_data,
):
    """Test finding database_provider_ingestions with pagination and sorting"""
    # Create multiple database_provider_ingestions

    database_provider = await database_provider_service.add(
        sample_database_provider_ingestion_data[1]
    )

    sample_database_provider_ingestion_data[0].provider_id = database_provider.id
    if database_provider.id is not None:
        database_provider_ingestions_to_create = [
            DatabaseProviderIngestionCreateSchema(
                name="Homolog ingestion",
                provider_id=database_provider.id,
                type="ingestion",
                include_schema=".+",
                exclude_database="public.*"
            )
            for i in range(3)
        ]

        for (
            database_provider_ingestion_data
        ) in database_provider_ingestions_to_create:
            await database_provider_ingestion_service.add(
                database_provider_ingestion_data
            )

        opts = DatabaseProviderIngestionQuerySchema(
            sort_by="name",
            sort_order="asc",
            page_size=2,
        )
        found_database_provider_ingestions = (
            await database_provider_ingestion_service.find(opts)
        )

        assert len(found_database_provider_ingestions.items) == 2
        (database_provider_ingestion1, database_provider_ingestion2) = (
            found_database_provider_ingestions.items
        )
        assert (
            database_provider_ingestion1.name is not None
            and database_provider_ingestion2.name is not None
            and database_provider_ingestion1.name
            <= database_provider_ingestion2.name
        )


@pytest.mark.asyncio
async def test_get_nonexistent_database_provider_ingestion(
    database_provider_ingestion_service,
):
    """Test retrieving a non-existent database_provider_ingestion"""
    non_existent_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundException) as nfe:
        (await database_provider_ingestion_service.get(non_existent_id))
    assert "not found" in str(nfe.value)


@pytest.mark.asyncio
async def test_update_nonexistent_database_provider_ingestion(
    database_provider_ingestion_service,
    sample_database_provider_ingestion_data,
):
    """Test updating a non-existent database_provider_ingestion"""
    non_existent_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundException) as nfe:
        (
            await database_provider_ingestion_service.update(
                non_existent_id, sample_database_provider_ingestion_data[0]
            )
        )
    assert "not found" in str(nfe.value)
