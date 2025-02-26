from unittest.mock import AsyncMock
import uuid

import pytest
from fastapi import status

from app.schemas import (
    LayerItemSchema,
    LayerListSchema,
    PaginatedSchema,
)
from app.services.layer_service import LayerService


@pytest.mark.asyncio
async def test_add_layer(async_client, mock_layer_service):
    """Test creating a new Layer entry."""
    # Test data
    provider_id = str(uuid.uuid4())
    obj_id = uuid.uuid4()
    test_data = {
        "id": str(obj_id),
        "name": "Test Layer",
        "description": "Layer to be added",
        "fully_qualified_name": "sample.Layer",
        "display_name": "Displayed name",
        "provider_id": provider_id,
        "updated_by": "FIXME!!!",
    }

    # Expected response
    expected_response = LayerItemSchema(
        id=obj_id,
        name="Test Database",
        description="Database to be added",
    )

    # Configure the mock
    mock_layer_service.add.return_value = expected_response.model_dump()

    # Make the request
    response = await async_client.post("/layers/", json=test_data)

    # Assertions
    assert response.status_code == status.HTTP_201_CREATED, response.text
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=True
    )


@pytest.mark.asyncio
async def test_delete_layer(async_client, mock_layer_service, test_uuid):
    """Test deleting a Layer entry."""
    mock_layer_service.delete.return_value = None

    response = await async_client.delete(f"/layers/{test_uuid}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_layer_service.delete.assert_called_once_with(test_uuid)


@pytest.mark.asyncio
async def test_update_layer(async_client, mock_layer_service, test_uuid):
    """Test updating a Layer entry."""
    test_data = {"name": "Updated Layer"}

    expected_response = LayerItemSchema(
        id=test_uuid,
        name="Updated Database",
    )

    mock_layer_service.update.return_value = LayerItemSchema.model_validate(
        expected_response
    )

    response = await async_client.patch(f"/layers/{test_uuid}", json=test_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=True
    )
    mock_layer_service.update.assert_called_once()


@pytest.mark.asyncio
async def test_find_layers(async_client, mock_layer_service):
    """Test getting a list of Layer entries."""
    db_item = {
        "id": str(uuid.uuid4()),
        "name": "Test Layer",
        "display_name": "Test Layer",
        "created_at": "2023-01-01T00:00:00",
    }

    paginated_response = PaginatedSchema[LayerListSchema](
        items=[LayerListSchema.model_validate(db_item)],
        page=1,
        page_size=10,
        page_count=1,
        count=1,
    )

    mock_layer_service.find.return_value = paginated_response

    response = await async_client.get("/layers/?page=1&size=10")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 1
    assert len(response.json()["items"]) == 1

    assert response.json()["items"][0]["name"] == "Test Layer"
    mock_layer_service.find.assert_called_once()


@pytest.mark.asyncio
async def test_get_layer(async_client, mock_layer_service, test_uuid):
    """Test getting a specific Layer entry."""
    expected_response = LayerItemSchema(
        id=test_uuid,
        name="Test Database",
        deleted=None,
        description=None,
    )

    mock_layer_service.get.return_value = LayerItemSchema.model_validate(
        expected_response
    )

    response = await async_client.get(f"/layers/{test_uuid}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=False
    )
    mock_layer_service.get.assert_called_once_with(test_uuid)


@pytest.mark.asyncio
async def test_get_layer_not_found(async_client, mock_layer_service, test_uuid):
    """Test getting a non-existent Layer entry."""
    mock_layer_service.get.return_value = None

    response = await async_client.get(f"/layers/{test_uuid}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Item not found"}
    mock_layer_service.get.assert_called_once_with(test_uuid)


# Test Layer service dependency
@pytest.mark.asyncio
async def test_layer_service_dependency():
    """Test that the Layer service is properly initialized with session."""
    mock_session = AsyncMock()
    service = LayerService(mock_session)
    assert service.session == mock_session
