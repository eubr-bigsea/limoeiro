import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status

from ..schemas import (
    PaginatedSchema,
    DatabaseTableCreateSchema,
    DatabaseTableUpdateSchema,
    DatabaseTableItemSchema,
    DatabaseTableListSchema,
    DatabaseTableQuerySchema,
)
from ..services.database_table_service import DatabaseTableService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*

@router.post("/tables/",
    tags=["DatabaseTable"],
    response_model=DatabaseTableItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True)
async def add_database_table(
    database_table_data: DatabaseTableCreateSchema,
    db: AsyncSession = Depends(get_session)) -> DatabaseTableItemSchema:
    """
    Add a single instance of class DatabaseTable.

    :return: A JSON object containing a success message.
    :rtype: dict
    """
        
    database_table_data.updated_by = "FIXME!!!"

    return await DatabaseTableService(db).add(
        database_table_data)

@router.delete("/tables/{database_table_id}",
    tags=["DatabaseTable"],
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_tables(database_table_id: UUID,
    db: AsyncSession = Depends(get_session)) :
    """
    Delete a single instance of class DatabaseTable.

    :param database_table_id: The ID of the instance to delete.
    :type database_table_id: int
    :return: A JSON object containing a success message.
    :rtype: dict
    """
    await DatabaseTableService(db).delete(database_table_id)
    return

@router.patch("/tables/{database_table_id}",
    tags=["DatabaseTable"],
    response_model=DatabaseTableItemSchema,
    response_model_exclude_none=True)
async def update_tables(database_table_id: UUID,
    database_table_data: DatabaseTableUpdateSchema,
    db: AsyncSession = Depends(get_session)) -> DatabaseTableItemSchema:
    """
    Update a single instance of class DatabaseTable.

    :param database_table_id: The ID of the instance to update.
    :type database_table_id: int
    :return: A JSON object containing a success message.
    :rtype: dict
    """
        
    database_table_data.updated_by = "FIXME!!!"

    return await DatabaseTableService(db).update(
        database_table_id, database_table_data)

@router.get(
    "/tables/",
    tags=["DatabaseTable"],
    response_model=PaginatedSchema[DatabaseTableListSchema],
    response_model_exclude_none=True
)
async def find_tables(
    query_options: DatabaseTableQuerySchema = Depends(),
    db: AsyncSession = Depends(get_session)
) -> PaginatedSchema[DatabaseTableListSchema]:
    """
    Retrieve a list of instances using query options.
    :param query_options: Query options for sorting, filtering and paging.
    :return: A JSON object containing the list of instances data.
    :rtype: dict
    """
    tables = await DatabaseTableService(db).find(query_options)
    model = DatabaseTableListSchema()
    tables.items = [model.model_validate(d) for d in tables.items]
    return tables

@router.get("/tables/{database_table_id}",
    tags=["DatabaseTable"],
    response_model=DatabaseTableItemSchema,
    response_model_exclude_none=False)
async def get_database_table(database_table_id: UUID,
    db: AsyncSession = Depends(get_session)) -> DatabaseTableItemSchema:
    """
    Retrieve a single instance of class DatabaseTable.

    :param database_table_id: The ID of the instance to retrieve.
    :type database_table_id: int
    :return: A JSON object containing the DatabaseTable instance data.
    :rtype: dict
    """

    database_table = await DatabaseTableService(db).get(
        database_table_id)
    if database_table is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return database_table
