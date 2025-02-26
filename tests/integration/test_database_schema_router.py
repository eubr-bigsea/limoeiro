from unittest.mock import AsyncMock
import uuid
from datetime import datetime

import pytest
from fastapi import status

from app.schemas import (
    DatabaseSchemaItemSchema,
    DatabaseSchemaListSchema,
    PaginatedSchema,
)
from app.services.database_schema_service import DatabaseSchemaService

_ref_date = "2025-02-28T00:00:02"


@pytest.mark.asyncio
async def test_add_database_schema(async_client, mock_database_schema_service):
    """Test creating a new DatabaseSchema entry."""
    # Test data
    provider_id = str(uuid.uuid4())
    obj_id = uuid.uuid4()
    test_data = {
        "id": str(obj_id),
        "name": "Test DatabaseSchema",
        "description": "DatabaseSchema to be added",
        "fully_qualified_name": "sample.DatabaseSchema",
        "display_name": "Displayed name",
        "provider_id": provider_id,
        "updated_by": "FIXME!!!",
        "database_id": str(obj_id),
    }

    # Expected response
    expected_response = DatabaseSchemaItemSchema(
        id=obj_id,
        name="Test Database",
        description="Database to be added",
        fully_qualified_name="sample.Database",
        display_name="Displayed name",
        updated_at=datetime.strptime(_ref_date, "%Y-%m-%dT%H:%M:%S"),
        updated_by="FIXME!!!",
    )

    # Configure the mock
    mock_database_schema_service.add.return_value = (
        expected_response.model_dump()
    )

    # Make the request
    response = await async_client.post("/schemas/", json=test_data)

    # Assertions
    assert response.status_code == status.HTTP_201_CREATED, response.text
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=True
    )


@pytest.mark.asyncio
async def test_delete_database_schema(
    async_client, mock_database_schema_service, test_uuid
):
    """Test deleting a DatabaseSchema entry."""
    mock_database_schema_service.delete.return_value = None

    response = await async_client.delete(f"/schemas/{test_uuid}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_database_schema_service.delete.assert_called_once_with(test_uuid)


@pytest.mark.asyncio
async def test_update_database_schema(
    async_client, mock_database_schema_service, test_uuid
):
    """Test updating a DatabaseSchema entry."""
    test_data = {"name": "Updated DatabaseSchema"}

    expected_response = DatabaseSchemaItemSchema(
        id=test_uuid,
        name="Updated Database",
        updated_at=datetime.strptime(_ref_date, "%Y-%m-%dT%H:%M:%S"),
        updated_by="FIXME!!!",
    )

    mock_database_schema_service.update.return_value = (
        DatabaseSchemaItemSchema.model_validate(expected_response)
    )

    response = await async_client.patch(f"/schemas/{test_uuid}", json=test_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=True
    )
    mock_database_schema_service.update.assert_called_once()


@pytest.mark.asyncio
async def test_find_database_schemas(async_client, mock_database_schema_service):
    """Test getting a list of DatabaseSchema entries."""
    db_item = {
        "id": str(uuid.uuid4()),
        "name": "Test DatabaseSchema",
        "display_name": "Test DatabaseSchema",
        "created_at": "2023-01-01T00:00:00",
    }

    paginated_response = PaginatedSchema[DatabaseSchemaListSchema](
        items=[DatabaseSchemaListSchema.model_validate(db_item)],
        page=1,
        page_size=10,
        page_count=1,
        count=1,
    )

    mock_database_schema_service.find.return_value = paginated_response

    response = await async_client.get("/schemas/?page=1&size=10")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 1
    assert len(response.json()["items"]) == 1

    assert response.json()["items"][0]["display_name"] == "Test DatabaseSchema"
    mock_database_schema_service.find.assert_called_once()


@pytest.mark.asyncio
async def test_get_database_schema(
    async_client, mock_database_schema_service, test_uuid
):
    """Test getting a specific DatabaseSchema entry."""
    expected_response = DatabaseSchemaItemSchema(
        id=test_uuid,
        name="Test Database",
        updated_at=datetime.strptime(_ref_date, "%Y-%m-%dT%H:%M:%S"),
        updated_by="admin",
        deleted=None,
        description=None,
        display_name=None,
        fully_qualified_name=None,
        href=None,
        layer=None,
        owner=None,
        version=None,
    )

    mock_database_schema_service.get.return_value = (
        DatabaseSchemaItemSchema.model_validate(expected_response)
    )

    response = await async_client.get(f"/schemas/{test_uuid}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response.model_dump(
        mode="json", exclude_none=False
    )
    mock_database_schema_service.get.assert_called_once_with(test_uuid)


@pytest.mark.asyncio
async def test_get_database_schema_not_found(
    async_client, mock_database_schema_service, test_uuid
):
    """Test getting a non-existent DatabaseSchema entry."""
    mock_database_schema_service.get.return_value = None

    response = await async_client.get(f"/schemas/{test_uuid}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Item not found"}
    mock_database_schema_service.get.assert_called_once_with(test_uuid)


# Test DatabaseSchema service dependency
@pytest.mark.asyncio
async def test_database_schema_service_dependency():
    """Test that the DatabaseSchema service is properly initialized with session."""
    mock_session = AsyncMock()
    service = DatabaseSchemaService(mock_session)
    assert service.session == mock_session
