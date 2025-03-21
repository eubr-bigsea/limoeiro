from unittest.mock import AsyncMock
import uuid
from datetime import datetime

import pytest
from fastapi import status

from app.schemas import (
    AIModelItemSchema,
    AIModelListSchema,
    PaginatedSchema,
)
from app.services.a_i_model_service import AIModelService

_ref_date = "2025-02-28T00:00:02"


@pytest.mark.asyncio
async def test_add_a_i_model(async_client, mock_a_i_model_service):
    """Test creating a new AIModel entry."""
    # Test data
    provider_id = str(uuid.uuid4())
    obj_id = uuid.uuid4()
    test_data = {
        "id": str(obj_id),
        "name": "Test AIModel",
        "description": "AIModel to be added",
        "fully_qualified_name": "sample.AIModel",
        "display_name": "Displayed name",
        "provider_id": provider_id,
        "updated_by": "FIXME!!!",
    }

    # Expected response
    expected_response = AIModelItemSchema(
        id=obj_id,
        name="Test Database",
        description="Database to be added",
        fully_qualified_name="sample.Database",
        display_name="Displayed name",
        updated_at=datetime.strptime(_ref_date, "%Y-%m-%dT%H:%M:%S"),
        updated_by="FIXME!!!",
    )

    # Configure the mock
    mock_a_i_model_service.add.return_value = expected_response.model_dump()

    # Make the request
    response = await async_client.post("/ai-models/", json=test_data)

    # Assertions
    assert response.status_code == status.HTTP_201_CREATED, response.text
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=True
    )


@pytest.mark.asyncio
async def test_delete_a_i_model(async_client, mock_a_i_model_service, test_uuid):
    """Test deleting a AIModel entry."""
    mock_a_i_model_service.delete.return_value = None

    response = await async_client.delete(f"/ai-models/{test_uuid}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_a_i_model_service.delete.assert_called_once_with(test_uuid)


@pytest.mark.asyncio
async def test_update_a_i_model(async_client, mock_a_i_model_service, test_uuid):
    """Test updating a AIModel entry."""
    test_data = {"name": "Updated AIModel"}

    expected_response = AIModelItemSchema(
        id=test_uuid,
        name="Updated Database",
        updated_at=datetime.strptime(_ref_date, "%Y-%m-%dT%H:%M:%S"),
        updated_by="FIXME!!!",
    )

    mock_a_i_model_service.update.return_value = (
        AIModelItemSchema.model_validate(expected_response)
    )

    response = await async_client.patch(
        f"/ai-models/{test_uuid}", json=test_data
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=True
    )
    mock_a_i_model_service.update.assert_called_once()


@pytest.mark.asyncio
async def test_find_a_i_models(async_client, mock_a_i_model_service):
    """Test getting a list of AIModel entries."""
    db_item = {
        "id": str(uuid.uuid4()),
        "name": "Test AIModel",
        "display_name": "Test AIModel",
        "created_at": "2023-01-01T00:00:00",
    }

    paginated_response = PaginatedSchema[AIModelListSchema](
        items=[AIModelListSchema.model_validate(db_item)],
        page=1,
        page_size=10,
        page_count=1,
        count=1,
    )

    mock_a_i_model_service.find.return_value = paginated_response

    response = await async_client.get("/ai-models/?page=1&size=10")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 1
    assert len(response.json()["items"]) == 1

    assert response.json()["items"][0]["display_name"] == "Test AIModel"
    mock_a_i_model_service.find.assert_called_once()


@pytest.mark.asyncio
async def test_get_a_i_model(async_client, mock_a_i_model_service, test_uuid):
    """Test getting a specific AIModel entry."""
    expected_response = AIModelItemSchema(
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

    mock_a_i_model_service.get.return_value = AIModelItemSchema.model_validate(
        expected_response
    )

    response = await async_client.get(f"/ai-models/{test_uuid}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=False
    )
    mock_a_i_model_service.get.assert_called_once_with(test_uuid)


@pytest.mark.asyncio
async def test_get_a_i_model_not_found(
    async_client, mock_a_i_model_service, test_uuid
):
    """Test getting a non-existent AIModel entry."""
    mock_a_i_model_service.get.return_value = None

    response = await async_client.get(f"/ai-models/{test_uuid}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Item not found"}
    mock_a_i_model_service.get.assert_called_once_with(test_uuid)


# Test AIModel service dependency
@pytest.mark.asyncio
async def test_a_i_model_service_dependency():
    """Test that the AIModel service is properly initialized with session."""
    mock_session = AsyncMock()
    service = AIModelService(mock_session)
    assert service.session == mock_session
