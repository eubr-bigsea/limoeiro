import pytest
import uuid
from app.exceptions import EntityNotFoundException
from app.schemas import (
    DatabaseProviderConnectionCreateSchema,
    DatabaseProviderConnectionQuerySchema,
    DatabaseProviderConnectionUpdateSchema,
)
from app.services.database_provider_connection_service import (
    DatabaseProviderConnectionService,
)


@pytest.mark.asyncio
async def test_add_database_provider_connection(
    database_provider_connection_service,
    database_provider_service,
    sample_database_provider_connection_data,
):
    """Test adding a new database_provider_connection"""
    database_provider = await database_provider_service.add(
        sample_database_provider_connection_data[1]
    )

    sample_database_provider_connection_data[
        0
    ].provider_id = database_provider.id
    database_provider_connection = (
        await database_provider_connection_service.add(
            sample_database_provider_connection_data[0]
        )
    )

    assert database_provider_connection.id is not None
    assert (
        database_provider_connection.user_name
        == sample_database_provider_connection_data[0].user_name
    )
    assert (
        database_provider_connection.host
        == sample_database_provider_connection_data[0].host
    )
    assert (
        database_provider_connection.port
        == sample_database_provider_connection_data[0].port
    )


@pytest.mark.asyncio
async def test_get_database_provider_connection(
    database_provider_connection_service,
    database_provider_service,
    sample_database_provider_connection_data,
):
    """Test retrieving a database_provider_connection by ID"""
    database_provider = await database_provider_service.add(
        sample_database_provider_connection_data[1]
    )

    sample_database_provider_connection_data[
        0
    ].provider_id = database_provider.id
    created_database_provider_connection = (
        await database_provider_connection_service.add(
            sample_database_provider_connection_data[0]
        )
    )
    retrieved_database_provider_connection = (
        await database_provider_connection_service.get(
            created_database_provider_connection.id
        )
    )

    assert retrieved_database_provider_connection is not None
    assert (
        retrieved_database_provider_connection.id
        == created_database_provider_connection.id
    )
    assert (
        retrieved_database_provider_connection.host
        == sample_database_provider_connection_data[0].host
    )


@pytest.mark.asyncio
async def test_delete_database_provider_connection(
    database_provider_connection_service,
    database_provider_service,
    sample_database_provider_connection_data,
):
    """Test deleting a database_provider_connection"""
    database_provider = await database_provider_service.add(
        sample_database_provider_connection_data[1]
    )

    sample_database_provider_connection_data[
        0
    ].provider_id = database_provider.id

    created_database_provider_connection = (
        await database_provider_connection_service.add(
            sample_database_provider_connection_data[0]
        )
    )

    deleted_database_provider_connection = (
        await database_provider_connection_service.delete(
            created_database_provider_connection.id
        )
    )
    assert (
        deleted_database_provider_connection.id
        == created_database_provider_connection.id
    )
    with pytest.raises(EntityNotFoundException) as nfe:
        (
            await database_provider_connection_service.get(
                created_database_provider_connection.id
            )
        )
    assert "not found" in str(nfe.value)


@pytest.mark.asyncio
async def test_update_database_provider_connection(
    database_provider_connection_service,
    database_provider_service,
    sample_database_provider_connection_data,
):
    """Test updating a database_provider_connection"""

    database_provider = await database_provider_service.add(
        sample_database_provider_connection_data[1]
    )

    sample_database_provider_connection_data[
        0
    ].provider_id = database_provider.id
    created_database_provider_connection = (
        await database_provider_connection_service.add(
            sample_database_provider_connection_data[0]
        )
    )

    updated_data = DatabaseProviderConnectionUpdateSchema(
        user_name="master",
        password="lame",
        host="server.local",
        port=6455,
        database="default",
        extra_parameters="{}",
    )

    updated_database_provider_connection = (
        await database_provider_connection_service.update(
            created_database_provider_connection.id, updated_data
        )
    )

    assert updated_database_provider_connection is not None
    assert (
        updated_database_provider_connection.id
        == created_database_provider_connection.id
    )
    assert updated_database_provider_connection.host == updated_data.host
    assert (
        updated_database_provider_connection.user_name == updated_data.user_name
    )


@pytest.mark.asyncio
async def test_find_database_provider_connections(
    database_provider_connection_service: DatabaseProviderConnectionService,
    database_provider_service: DatabaseProviderConnectionService,
    sample_database_provider_connection_data,
):
    """Test finding database_provider_connections with pagination and sorting"""
    # Create multiple database_provider_connections

    database_provider = await database_provider_service.add(
        sample_database_provider_connection_data[1]
    )

    sample_database_provider_connection_data[
        0
    ].provider_id = database_provider.id
    if database_provider.id is not None:
        database_provider_connections_to_create = [
            DatabaseProviderConnectionCreateSchema(
                user_name="root",
                password="sorry",
                host=f"test.server {i}",
                port=5455,
                database="public",
                extra_parameters='{"teste": 1}',
                provider_id=database_provider.id,
            )
            for i in range(3)
        ]

        for (
            database_provider_connection_data
        ) in database_provider_connections_to_create:
            await database_provider_connection_service.add(
                database_provider_connection_data
            )

        opts = DatabaseProviderConnectionQuerySchema(
            sort_by="name",
            sort_order="asc",
            page_size=2,
        )
        found_database_provider_connections = (
            await database_provider_connection_service.find(opts)
        )

        assert len(found_database_provider_connections.items) == 2
        (database_provider_connection1, database_provider_connection2) = (
            found_database_provider_connections.items
        )
        assert (
            database_provider_connection1.host is not None
            and database_provider_connection2.host is not None
            and database_provider_connection1.host
            < database_provider_connection2.host
        )


@pytest.mark.asyncio
async def test_get_nonexistent_database_provider_connection(
    database_provider_connection_service,
):
    """Test retrieving a non-existent database_provider_connection"""
    non_existent_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundException) as nfe:
        (await database_provider_connection_service.get(non_existent_id))
    assert 'not found' in str(nfe.value)


@pytest.mark.asyncio
async def test_update_nonexistent_database_provider_connection(
    database_provider_connection_service,
    sample_database_provider_connection_data,
):
    """Test updating a non-existent database_provider_connection"""
    non_existent_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundException) as nfe:
        (
            await database_provider_connection_service.update(
                non_existent_id, sample_database_provider_connection_data[0]
            )
        )
    assert "not found" in str(nfe.value)
