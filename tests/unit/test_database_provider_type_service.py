import pytest
import uuid

from app.exceptions import EntityNotFoundException


@pytest.mark.asyncio
async def test_get_database_provider_type(
    database_provider_type_service, sample_database_provider_type_data
):
    """Test retrieving a database_provider_type by ID"""

    database_provider_type = await database_provider_type_service.get(
        "POSTGRESQL"
    )
    assert database_provider_type is not None
    assert database_provider_type.id == "POSTGRESQL"


@pytest.mark.asyncio
async def test_get_nonexistent_database_provider_type(
    database_provider_type_service,
):
    """Test retrieving a non-existent database_provider_type"""
    non_existent_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundException) as nf:
        await database_provider_type_service.get(non_existent_id)
        assert str(nf) == "teste"
