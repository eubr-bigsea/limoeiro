from unittest.mock import AsyncMock
import uuid
from datetime import datetime

import pytest
from fastapi import status

from app.schemas import (
    DatabaseProviderTypeItemSchema,
    DatabaseProviderTypeListSchema,
    PaginatedSchema,
)
from app.services.database_provider_type_service import (
    DatabaseProviderTypeService,
)

_ref_date = "2025-02-28T00:00:02"


@pytest.mark.asyncio
async def test_find_database_provider_types(
    async_client, mock_database_provider_type_service
):
    """Test getting a list of DatabaseProviderType entries."""
    db_item = {
        "id": str(uuid.uuid4()),
        "name": "Test DatabaseProviderType",
        "display_name": "Test DatabaseProviderType",
        "created_at": "2023-01-01T00:00:00",
    }

    paginated_response = PaginatedSchema[DatabaseProviderTypeListSchema](
        items=[DatabaseProviderTypeListSchema.model_validate(db_item)],
        page=1,
        page_size=10,
        page_count=1,
        count=1,
    )

    mock_database_provider_type_service.find.return_value = paginated_response

    response = await async_client.get("/database-provider-types/?page=1&size=10")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 1
    assert len(response.json()["items"]) == 1

    assert (
        response.json()["items"][0]["display_name"]
        == "Test DatabaseProviderType"
    )
    mock_database_provider_type_service.find.assert_called_once()


@pytest.mark.asyncio
async def test_get_database_provider_type(
    async_client, mock_database_provider_type_service
):
    """Test getting a specific DatabaseProviderType entry."""
    provider_type_id = "fake_pgsql"
    expected_response = DatabaseProviderTypeItemSchema(
        id=provider_type_id,
        display_name="Displaying",
        image="https://test.com/test",
    )

    mock_database_provider_type_service.get.return_value = (
        DatabaseProviderTypeItemSchema.model_validate(expected_response)
    )

    response = await async_client.get(
        f"/database-provider-types/{provider_type_id}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=False
    )
    mock_database_provider_type_service.get.assert_called_once_with(
        provider_type_id)


@pytest.mark.asyncio
async def test_get_database_provider_type_not_found(
    async_client, mock_database_provider_type_service, test_uuid
):
    """Test getting a non-existent DatabaseProviderType entry."""
    provider_type_id = "fake_pgsql"
    mock_database_provider_type_service.get.return_value = None

    response = await async_client.get(f"/database-provider-types/{provider_type_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Item not found"}
    mock_database_provider_type_service.get.assert_called_once_with(provider_type_id)


# Test DatabaseProviderType service dependency
@pytest.mark.asyncio
async def test_database_provider_type_service_dependency():
    """Test that the DatabaseProviderType service is properly initialized with session."""
    mock_session = AsyncMock()
    service = DatabaseProviderTypeService(mock_session)
    assert service.session == mock_session
