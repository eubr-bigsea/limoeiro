import logging
import typing
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status

from ..schemas import (
    PaginatedSchema,
    DatabaseProviderCreateSchema,
    DatabaseProviderUpdateSchema,
    DatabaseProviderItemSchema,
    DatabaseProviderListSchema,
    DatabaseProviderQuerySchema,
)
from ..services.database_provider_service import DatabaseProviderService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*

@router.post("/database-providers/",
    tags=["DatabaseProvider"],
    response_model=DatabaseProviderItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True)
async def add_database_provider(
    database_provider_data: DatabaseProviderCreateSchema,
    db: AsyncSession = Depends(get_session)) -> DatabaseProviderItemSchema:
    """
    Add a single instance of class DatabaseProvider.

    :return: A JSON object containing a success message.
    :rtype: dict
    """
        
    database_provider_data.updated_by = "FIXME!!!"

    return await DatabaseProviderService(db).add(
        database_provider_data)

@router.delete("/database-providers/{database_provider_id}",
    tags=["DatabaseProvider"],
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_database_providers(database_provider_id: UUID,
    db: AsyncSession = Depends(get_session)) :
    """
    Delete a single instance of class DatabaseProvider.

    :param database_provider_id: The ID of the instance to delete.
    :type database_provider_id: int
    :return: A JSON object containing a success message.
    :rtype: dict
    """
    await DatabaseProviderService(db).delete(database_provider_id)
    return

@router.patch("/database-providers/{database_provider_id}",
    tags=["DatabaseProvider"],
    response_model=DatabaseProviderItemSchema,
    response_model_exclude_none=True)
async def update_database_providers(database_provider_id: UUID,
    database_provider_data: DatabaseProviderUpdateSchema,
    db: AsyncSession = Depends(get_session)) -> DatabaseProviderItemSchema:
    """
    Update a single instance of class DatabaseProvider.

    :param database_provider_id: The ID of the instance to update.
    :type database_provider_id: int
    :return: A JSON object containing a success message.
    :rtype: dict
    """
        
    database_provider_data.updated_by = "FIXME!!!"

    return await DatabaseProviderService(db).update(
        database_provider_id, database_provider_data)

@router.get(
    "/database-providers/",
    tags=["DatabaseProvider"],
    response_model=typing.List[DatabaseProviderListSchema],
    response_model_exclude_none=True
)
async def find_database_providers(
    query_options: DatabaseProviderQuerySchema = Depends(),
    db: AsyncSession = Depends(get_session)
) -> PaginatedSchema[DatabaseProviderListSchema]:
    """
    Retrieve a list of instances using query options.
    :param query_options: Query options for sorting, filtering and paging.
    :return: A JSON object containing the list of instances data.
    :rtype: dict
    """
    return await DatabaseProviderService(db).find(query_options)

@router.get("/database-providers/{database_provider_id}",
    tags=["DatabaseProvider"],
    response_model=DatabaseProviderItemSchema,
    response_model_exclude_none=False)
async def get_database_provider(database_provider_id: UUID,
    db: AsyncSession = Depends(get_session)) -> DatabaseProviderItemSchema:
    """
    Retrieve a single instance of class DatabaseProvider.

    :param database_provider_id: The ID of the instance to retrieve.
    :type database_provider_id: int
    :return: A JSON object containing the DatabaseProvider instance data.
    :rtype: dict
    """

    database_provider = await DatabaseProviderService(db).get(
        database_provider_id)
    if database_provider is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return database_provider
