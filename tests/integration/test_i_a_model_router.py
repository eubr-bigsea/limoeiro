from unittest.mock import AsyncMock
import uuid
from datetime import datetime

import pytest
from fastapi import status

from app.schemas import (
    IAModelItemSchema,
    IAModelListSchema,
    PaginatedSchema,
)
from app.services.i_a_model_service import IAModelService

_ref_date = "2025-02-28T00:00:02"


@pytest.mark.asyncio
async def test_add_i_a_model(async_client, mock_i_a_model_service):
    """Test creating a new IAModel entry."""
    # Test data
    provider_id = str(uuid.uuid4())
    obj_id = uuid.uuid4()
    test_data = {
        "id": str(obj_id),
        "name": "Test IAModel",
        "description": "IAModel to be added",
        "fully_qualified_name": "sample.IAModel",
        "display_name": "Displayed name",
        "provider_id": provider_id,
        "updated_by": "FIXME!!!",
    }

    # Expected response
    expected_response = IAModelItemSchema(
        id=obj_id,
        name="Test Database",
        description="Database to be added",
        fully_qualified_name="sample.Database",
        display_name="Displayed name",
        updated_at=datetime.strptime(_ref_date, "%Y-%m-%dT%H:%M:%S"),
        updated_by="FIXME!!!",
    )

    # Configure the mock
    mock_i_a_model_service.add.return_value = expected_response.model_dump()

    # Make the request
    response = await async_client.post("/ia-models/", json=test_data)

    # Assertions
    assert response.status_code == status.HTTP_201_CREATED, response.text
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=True
    )


@pytest.mark.asyncio
async def test_delete_i_a_model(async_client, mock_i_a_model_service, test_uuid):
    """Test deleting a IAModel entry."""
    mock_i_a_model_service.delete.return_value = None

    response = await async_client.delete(f"/ia-models/{test_uuid}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_i_a_model_service.delete.assert_called_once_with(test_uuid)


@pytest.mark.asyncio
async def test_update_i_a_model(async_client, mock_i_a_model_service, test_uuid):
    """Test updating a IAModel entry."""
    test_data = {"name": "Updated IAModel"}

    expected_response = IAModelItemSchema(
        id=test_uuid,
        name="Updated Database",
        updated_at=datetime.strptime(_ref_date, "%Y-%m-%dT%H:%M:%S"),
        updated_by="FIXME!!!",
    )

    mock_i_a_model_service.update.return_value = (
        IAModelItemSchema.model_validate(expected_response)
    )

    response = await async_client.patch(
        f"/ia-models/{test_uuid}", json=test_data
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=True
    )
    mock_i_a_model_service.update.assert_called_once()


@pytest.mark.asyncio
async def test_find_i_a_models(async_client, mock_i_a_model_service):
    """Test getting a list of IAModel entries."""
    db_item = {
        "id": str(uuid.uuid4()),
        "name": "Test IAModel",
        "display_name": "Test IAModel",
        "created_at": "2023-01-01T00:00:00",
    }

    paginated_response = PaginatedSchema[IAModelListSchema](
        items=[IAModelListSchema.model_validate(db_item)],
        page=1,
        page_size=10,
        page_count=1,
        count=1,
    )

    mock_i_a_model_service.find.return_value = paginated_response

    response = await async_client.get("/ia-models/?page=1&size=10")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 1
    assert len(response.json()["items"]) == 1

    assert response.json()["items"][0]["display_name"] == "Test IAModel"
    mock_i_a_model_service.find.assert_called_once()


@pytest.mark.asyncio
async def test_get_i_a_model(async_client, mock_i_a_model_service, test_uuid):
    """Test getting a specific IAModel entry."""
    expected_response = IAModelItemSchema(
        id=test_uuid,
        name="Test Database",
        updated_at=datetime.strptime(_ref_date, "%Y-%m-%dT%H:%M:%S"),
        updated_by="admin",
        deleted=None,
        description=None,
        display_name=None,
        domain=None,
        fully_qualified_name=None,
        href=None,
        owner=None,
        version=None,
    )

    mock_i_a_model_service.get.return_value = IAModelItemSchema.model_validate(
        expected_response
    )

    response = await async_client.get(f"/ia-models/{test_uuid}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=False
    )
    mock_i_a_model_service.get.assert_called_once_with(test_uuid)


@pytest.mark.asyncio
async def test_get_i_a_model_not_found(
    async_client, mock_i_a_model_service, test_uuid
):
    """Test getting a non-existent IAModel entry."""
    mock_i_a_model_service.get.return_value = None

    response = await async_client.get(f"/ia-models/{test_uuid}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Item not found"}
    mock_i_a_model_service.get.assert_called_once_with(test_uuid)


# Test IAModel service dependency
@pytest.mark.asyncio
async def test_i_a_model_service_dependency():
    """Test that the IAModel service is properly initialized with session."""
    mock_session = AsyncMock()
    service = IAModelService(mock_session)
    assert service.session == mock_session
