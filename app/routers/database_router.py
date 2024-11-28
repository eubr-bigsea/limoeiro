import logging
import typing
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status

from ..schemas import (
    PaginatedSchema,
    DatabaseCreateSchema,
    DatabaseUpdateSchema,
    DatabaseItemSchema,
    DatabaseListSchema,
    DatabaseQuerySchema,
)
from ..services.database_service import DatabaseService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*

@router.post("/databases/",
    tags=["Database"],
    response_model=DatabaseItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True)
async def add_database(
    database_data: DatabaseCreateSchema,
    db: AsyncSession = Depends(get_session)) -> DatabaseItemSchema:
    """
    Add a single instance of class Database.

    :return: A JSON object containing a success message.
    :rtype: dict
    """
        
    database_data.updated_by = "FIXME!!!"

    return await DatabaseService(db).add(
        database_data)

@router.delete("/databases/{database_id}",
    tags=["Database"],
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_databases(database_id: UUID,
    db: AsyncSession = Depends(get_session)) :
    """
    Delete a single instance of class Database.

    :param database_id: The ID of the instance to delete.
    :type database_id: int
    :return: A JSON object containing a success message.
    :rtype: dict
    """
    await DatabaseService(db).delete(database_id)
    return

@router.patch("/databases/{database_id}",
    tags=["Database"],
    response_model=DatabaseItemSchema,
    response_model_exclude_none=True)
async def update_databases(database_id: UUID,
    database_data: DatabaseUpdateSchema,
    db: AsyncSession = Depends(get_session)) -> DatabaseItemSchema:
    """
    Update a single instance of class Database.

    :param database_id: The ID of the instance to update.
    :type database_id: int
    :return: A JSON object containing a success message.
    :rtype: dict
    """
        
    database_data.updated_by = "FIXME!!!"

    return await DatabaseService(db).update(
        database_id, database_data)

@router.get(
    "/databases/",
    tags=["Database"],
    response_model=typing.List[DatabaseListSchema],
    response_model_exclude_none=True
)
async def find_databases(
    query_options: DatabaseQuerySchema = Depends(),
    db: AsyncSession = Depends(get_session)
) -> PaginatedSchema[DatabaseListSchema]:
    """
    Retrieve a list of instances using query options.
    :param query_options: Query options for sorting, filtering and paging.
    :return: A JSON object containing the list of instances data.
    :rtype: dict
    """
    return await DatabaseService(db).find(query_options)

@router.get("/databases/{database_id}",
    tags=["Database"],
    response_model=DatabaseItemSchema,
    response_model_exclude_none=False)
async def get_database(database_id: UUID,
    db: AsyncSession = Depends(get_session)) -> DatabaseItemSchema:
    """
    Retrieve a single instance of class Database.

    :param database_id: The ID of the instance to retrieve.
    :type database_id: int
    :return: A JSON object containing the Database instance data.
    :rtype: dict
    """

    database = await DatabaseService(db).get(
        database_id)
    if database is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return database
