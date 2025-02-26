from unittest.mock import AsyncMock
import uuid

import pytest
from fastapi import status

from app.schemas import (
    DomainItemSchema,
    DomainListSchema,
    PaginatedSchema,
)
from app.services.domain_service import DomainService


@pytest.mark.asyncio
async def test_add_domain(async_client, mock_domain_service):
    """Test creating a new Domain entry."""
    # Test data
    provider_id = str(uuid.uuid4())
    obj_id = uuid.uuid4()
    test_data = {
        "id": str(obj_id),
        "name": "Test Domain",
        "description": "Domain to be added",
        "fully_qualified_name": "sample.Domain",
        "display_name": "Displayed name",
        "provider_id": provider_id,
        "updated_by": "FIXME!!!",
    }

    # Expected response
    expected_response = DomainItemSchema(
        id=obj_id,
        name="Test Database",
        description="Database to be added",
    )

    # Configure the mock
    mock_domain_service.add.return_value = expected_response.model_dump()

    # Make the request
    response = await async_client.post("/domains/", json=test_data)

    # Assertions
    assert response.status_code == status.HTTP_201_CREATED, response.text
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=True
    )


@pytest.mark.asyncio
async def test_delete_domain(async_client, mock_domain_service, test_uuid):
    """Test deleting a Domain entry."""
    mock_domain_service.delete.return_value = None

    response = await async_client.delete(f"/domains/{test_uuid}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_domain_service.delete.assert_called_once_with(test_uuid)


@pytest.mark.asyncio
async def test_update_domain(async_client, mock_domain_service, test_uuid):
    """Test updating a Domain entry."""
    test_data = {"name": "Updated Domain"}

    expected_response = DomainItemSchema(
        id=test_uuid,
        name="Updated Database",
    )

    mock_domain_service.update.return_value = DomainItemSchema.model_validate(
        expected_response
    )

    response = await async_client.patch(f"/domains/{test_uuid}", json=test_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=True
    )
    mock_domain_service.update.assert_called_once()


@pytest.mark.asyncio
async def test_find_domains(async_client, mock_domain_service):
    """Test getting a list of Domain entries."""
    db_item = {
        "id": str(uuid.uuid4()),
        "name": "Test Domain",
        "display_name": "Test Domain",
        "created_at": "2023-01-01T00:00:00",
    }

    paginated_response = PaginatedSchema[DomainListSchema](
        items=[DomainListSchema.model_validate(db_item)],
        page=1,
        page_size=10,
        page_count=1,
        count=1,
    )

    mock_domain_service.find.return_value = paginated_response

    response = await async_client.get("/domains/?page=1&size=10")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 1
    assert len(response.json()["items"]) == 1

    assert response.json()["items"][0]["name"] == "Test Domain"
    mock_domain_service.find.assert_called_once()


@pytest.mark.asyncio
async def test_get_domain(async_client, mock_domain_service, test_uuid):
    """Test getting a specific Domain entry."""
    expected_response = DomainItemSchema(
        id=test_uuid,
        name="Test Database",
        deleted=None,
        description=None,
    )

    mock_domain_service.get.return_value = DomainItemSchema.model_validate(
        expected_response
    )

    response = await async_client.get(f"/domains/{test_uuid}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=False
    )
    mock_domain_service.get.assert_called_once_with(test_uuid)


@pytest.mark.asyncio
async def test_get_domain_not_found(
    async_client, mock_domain_service, test_uuid
):
    """Test getting a non-existent Domain entry."""
    mock_domain_service.get.return_value = None

    response = await async_client.get(f"/domains/{test_uuid}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Item not found"}
    mock_domain_service.get.assert_called_once_with(test_uuid)


# Test Domain service dependency
@pytest.mark.asyncio
async def test_domain_service_dependency():
    """Test that the Domain service is properly initialized with session."""
    mock_session = AsyncMock()
    service = DomainService(mock_session)
    assert service.session == mock_session
