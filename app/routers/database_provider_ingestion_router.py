import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status

from ..schemas import (
    PaginatedSchema,
    DatabaseProviderIngestionCreateSchema,
    DatabaseProviderIngestionUpdateSchema,
    DatabaseProviderIngestionItemSchema,
    DatabaseProviderIngestionListSchema,
    DatabaseProviderIngestionQuerySchema,
)
from ..services.database_provider_ingestion_service import DatabaseProviderIngestionService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*

@router.post("/ingestions/",
    tags=["DatabaseProviderIngestion"],
    response_model=DatabaseProviderIngestionItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True)
async def add_database_provider_ingestion(
    database_provider_ingestion_data: DatabaseProviderIngestionCreateSchema,
    db: AsyncSession = Depends(get_session)) -> DatabaseProviderIngestionItemSchema:
    """
    Add a single instance of class DatabaseProviderIngestion.

    :return: A JSON object containing a success message.
    :rtype: dict
    """
        
    database_provider_ingestion_data.updated_by = "FIXME!!!"

    return await DatabaseProviderIngestionService(db).add(
        database_provider_ingestion_data)

@router.delete("/ingestions/{database_provider_ingestion_id}",
    tags=["DatabaseProviderIngestion"],
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_ingestions(database_provider_ingestion_id: UUID,
    db: AsyncSession = Depends(get_session)) :
    """
    Delete a single instance of class DatabaseProviderIngestion.

    :param database_provider_ingestion_id: The ID of the instance to delete.
    :type database_provider_ingestion_id: int
    :return: A JSON object containing a success message.
    :rtype: dict
    """
    await DatabaseProviderIngestionService(db).delete(database_provider_ingestion_id)
    return

@router.patch("/ingestions/{database_provider_ingestion_id}",
    tags=["DatabaseProviderIngestion"],
    response_model=DatabaseProviderIngestionItemSchema,
    response_model_exclude_none=True)
async def update_ingestions(database_provider_ingestion_id: UUID,
    database_provider_ingestion_data: DatabaseProviderIngestionUpdateSchema,
    db: AsyncSession = Depends(get_session)) -> DatabaseProviderIngestionItemSchema:
    """
    Update a single instance of class DatabaseProviderIngestion.

    :param database_provider_ingestion_id: The ID of the instance to update.
    :type database_provider_ingestion_id: int
    :return: A JSON object containing a success message.
    :rtype: dict
    """
        
    database_provider_ingestion_data.updated_by = "FIXME!!!"

    return await DatabaseProviderIngestionService(db).update(
        database_provider_ingestion_id, database_provider_ingestion_data)

@router.get(
    "/ingestions/",
    tags=["DatabaseProviderIngestion"],
    response_model=PaginatedSchema[DatabaseProviderIngestionListSchema],
    response_model_exclude_none=True
)
async def find_ingestions(
    query_options: DatabaseProviderIngestionQuerySchema = Depends(),
    db: AsyncSession = Depends(get_session)
) -> PaginatedSchema[DatabaseProviderIngestionListSchema]:
    """
    Retrieve a list of instances using query options.
    :param query_options: Query options for sorting, filtering and paging.
    :return: A JSON object containing the list of instances data.
    :rtype: dict
    """
    ingestions = await DatabaseProviderIngestionService(db).find(query_options)
    model = DatabaseProviderIngestionListSchema()
    ingestions.items = [model.model_validate(d) for d in ingestions.items]
    return ingestions

@router.get("/ingestions/{database_provider_ingestion_id}",
    tags=["DatabaseProviderIngestion"],
    response_model=DatabaseProviderIngestionItemSchema,
    response_model_exclude_none=False)
async def get_database_provider_ingestion(database_provider_ingestion_id: UUID,
    db: AsyncSession = Depends(get_session)) -> DatabaseProviderIngestionItemSchema:
    """
    Retrieve a single instance of class DatabaseProviderIngestion.

    :param database_provider_ingestion_id: The ID of the instance to retrieve.
    :type database_provider_ingestion_id: int
    :return: A JSON object containing the DatabaseProviderIngestion instance data.
    :rtype: dict
    """

    database_provider_ingestion = await DatabaseProviderIngestionService(db).get(
        database_provider_ingestion_id)
    if database_provider_ingestion is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return database_provider_ingestion
