import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status

from ..schemas import (
    PaginatedSchema,
    DatabaseSchemaCreateSchema,
    DatabaseSchemaUpdateSchema,
    DatabaseSchemaItemSchema,
    DatabaseSchemaListSchema,
    DatabaseSchemaQuerySchema,
)
from ..services.database_schema_service import DatabaseSchemaService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*

@router.post("/schemas/",
    tags=["DatabaseSchema"],
    response_model=DatabaseSchemaItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True)
async def add_database_schema(
    database_schema_data: DatabaseSchemaCreateSchema,
    db: AsyncSession = Depends(get_session)) -> DatabaseSchemaItemSchema:
    """
    Add a single instance of class DatabaseSchema.

    :return: A JSON object containing a success message.
    :rtype: dict
    """
        
    database_schema_data.updated_by = "FIXME!!!"

    return await DatabaseSchemaService(db).add(
        database_schema_data)

@router.delete("/schemas/{database_schema_id}",
    tags=["DatabaseSchema"],
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_schemas(database_schema_id: UUID,
    db: AsyncSession = Depends(get_session)) :
    """
    Delete a single instance of class DatabaseSchema.

    :param database_schema_id: The ID of the instance to delete.
    :type database_schema_id: int
    :return: A JSON object containing a success message.
    :rtype: dict
    """
    await DatabaseSchemaService(db).delete(database_schema_id)
    return

@router.patch("/schemas/{database_schema_id}",
    tags=["DatabaseSchema"],
    response_model=DatabaseSchemaItemSchema,
    response_model_exclude_none=True)
async def update_schemas(database_schema_id: UUID,
    database_schema_data: DatabaseSchemaUpdateSchema,
    db: AsyncSession = Depends(get_session)) -> DatabaseSchemaItemSchema:
    """
    Update a single instance of class DatabaseSchema.

    :param database_schema_id: The ID of the instance to update.
    :type database_schema_id: int
    :return: A JSON object containing a success message.
    :rtype: dict
    """
        
    database_schema_data.updated_by = "FIXME!!!"

    return await DatabaseSchemaService(db).update(
        database_schema_id, database_schema_data)

@router.get(
    "/schemas/",
    tags=["DatabaseSchema"],
    response_model=PaginatedSchema[DatabaseSchemaListSchema],
    response_model_exclude_none=True
)
async def find_schemas(
    query_options: DatabaseSchemaQuerySchema = Depends(),
    db: AsyncSession = Depends(get_session)
) -> PaginatedSchema[DatabaseSchemaListSchema]:
    """
    Retrieve a list of instances using query options.
    :param query_options: Query options for sorting, filtering and paging.
    :return: A JSON object containing the list of instances data.
    :rtype: dict
    """
    schemas = await DatabaseSchemaService(db).find(query_options)
    model = DatabaseSchemaListSchema()
    schemas.items = [model.model_validate(d) for d in schemas.items]
    return schemas

@router.get("/schemas/{database_schema_id}",
    tags=["DatabaseSchema"],
    response_model=DatabaseSchemaItemSchema,
    response_model_exclude_none=False)
async def get_database_schema(database_schema_id: UUID,
    db: AsyncSession = Depends(get_session)) -> DatabaseSchemaItemSchema:
    """
    Retrieve a single instance of class DatabaseSchema.

    :param database_schema_id: The ID of the instance to retrieve.
    :type database_schema_id: int
    :return: A JSON object containing the DatabaseSchema instance data.
    :rtype: dict
    """

    database_schema = await DatabaseSchemaService(db).get(
        database_schema_id)
    if database_schema is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return database_schema
