# 
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status, Path

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
    Adiciona uma instância da classe DatabaseProviderIngestion.
    """
    return await DatabaseProviderIngestionService(db).add(
        database_provider_ingestion_data)

@router.delete("/ingestions/{database_provider_ingestion_id}",
    tags=["DatabaseProviderIngestion"],
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_ingestions(database_provider_ingestion_id: UUID,
    db: AsyncSession = Depends(get_session)) :
    """
    Exclui uma instância da classe DatabaseProviderIngestion.
    """
    await DatabaseProviderIngestionService(db).delete(database_provider_ingestion_id)
    return

@router.patch("/ingestions/{database_provider_ingestion_id}",
    tags=["DatabaseProviderIngestion"],
    response_model=DatabaseProviderIngestionItemSchema,
    response_model_exclude_none=True)
async def update_ingestions(database_provider_ingestion_id: UUID=Path(..., description="Identificador"),
    database_provider_ingestion_data: DatabaseProviderIngestionUpdateSchema=None,
    db: AsyncSession = Depends(get_session)) -> DatabaseProviderIngestionItemSchema:
    """
    Atualiza uma instância da classe DatabaseProviderIngestion.
    """
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
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    ingestions = await DatabaseProviderIngestionService(db).find(query_options)
    model = DatabaseProviderIngestionListSchema()
    ingestions.items = [model.model_validate(d) for d in ingestions.items]
    return ingestions

@router.get("/ingestions/{database_provider_ingestion_id}",
    tags=["DatabaseProviderIngestion"],
    response_model=DatabaseProviderIngestionItemSchema,
    response_model_exclude_none=False)
async def get_database_provider_ingestion(database_provider_ingestion_id: UUID = Path(..., description="Identificador"),
    db: AsyncSession = Depends(get_session)) -> DatabaseProviderIngestionItemSchema:
    """
    Recupera uma instância da classe DatabaseProviderIngestion.
    """

    database_provider_ingestion = await DatabaseProviderIngestionService(db).get(
        database_provider_ingestion_id)
    if database_provider_ingestion is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return database_provider_ingestion
