import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import status

from app.schemas import (
    PaginatedSchema,
    TagItemSchema,
    TagListSchema,
)
from app.services.tag_service import TagService


@pytest.mark.asyncio
async def test_add_tag(async_client, mock_tag_service):
    """Test creating a new Tag entry."""
    # Test data
    provider_id = str(uuid.uuid4())
    obj_id = uuid.uuid4()
    test_data = {
        "id": str(obj_id),
        "name": "Test Tag",
        "description": "Tag to be added",
        "fully_qualified_name": "sample.Tag",
        "display_name": "Displayed name",
        "provider_id": provider_id,
        "updated_by": "FIXME!!!",
    }

    # Expected response
    expected_response = TagItemSchema(
        id=obj_id,
        name="Test Database",
        description="Database to be added",
    )

    # Configure the mock
    mock_tag_service.add.return_value = expected_response.model_dump()

    # Make the request
    response = await async_client.post("/tags/", json=test_data)

    # Assertions
    assert response.status_code == status.HTTP_201_CREATED, response.text
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=True
    )


@pytest.mark.asyncio
async def test_delete_tag(async_client, mock_tag_service, test_uuid):
    """Test deleting a Tag entry."""
    mock_tag_service.delete.return_value = None

    response = await async_client.delete(f"/tags/{test_uuid}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_tag_service.delete.assert_called_once_with(test_uuid)


@pytest.mark.asyncio
async def test_update_tag(async_client, mock_tag_service, test_uuid):
    """Test updating a Tag entry."""
    test_data = {"name": "Updated Tag"}

    expected_response = TagItemSchema(
        id=test_uuid,
        name="Updated Database",
    )

    mock_tag_service.update.return_value = TagItemSchema.model_validate(
        expected_response
    )

    response = await async_client.patch(f"/tags/{test_uuid}", json=test_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=True
    )
    mock_tag_service.update.assert_called_once()


@pytest.mark.asyncio
async def test_find_tags(async_client, mock_tag_service):
    """Test getting a list of Tag entries."""
    db_item = {
        "id": str(uuid.uuid4()),
        "name": "Test Tag",
        "display_name": "Test Tag",
        "created_at": "2023-01-01T00:00:00",
    }

    paginated_response = PaginatedSchema[TagListSchema](
        items=[TagListSchema.model_validate(db_item)],
        page=1,
        page_size=10,
        page_count=1,
        count=1,
    )

    mock_tag_service.find.return_value = paginated_response

    response = await async_client.get("/tags/?page=1&size=10")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 1
    assert len(response.json()["items"]) == 1

    assert response.json()["items"][0]["name"] == "Test Tag"
    mock_tag_service.find.assert_called_once()


@pytest.mark.asyncio
async def test_get_tag(async_client, mock_tag_service, test_uuid):
    """Test getting a specific Tag entry."""
    expected_response = TagItemSchema(
        id=test_uuid,
        name="Test Database",
        deleted=None,
        description=None,
    )

    mock_tag_service.get.return_value = TagItemSchema.model_validate(
        expected_response
    )

    response = await async_client.get(f"/tags/{test_uuid}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=False
    )
    mock_tag_service.get.assert_called_once_with(test_uuid)


@pytest.mark.asyncio
async def test_get_tag_not_found(async_client, mock_tag_service, test_uuid):
    """Test getting a non-existent Tag entry."""
    mock_tag_service.get.return_value = None

    response = await async_client.get(f"/tags/{test_uuid}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Item not found"}
    mock_tag_service.get.assert_called_once_with(test_uuid)


# Test Tag service dependency
@pytest.mark.asyncio
async def test_tag_service_dependency():
    """Test that the Tag service is properly initialized with session."""
    mock_session = AsyncMock()
    service = TagService(mock_session)
    assert service.session == mock_session
