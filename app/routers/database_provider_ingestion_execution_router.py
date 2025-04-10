#
import logging
import typing
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status, Path

from ..schemas import (
    PaginatedSchema,
    DatabaseProviderIngestionExecutionCreateSchema,
    DatabaseProviderIngestionExecutionUpdateSchema,
    DatabaseProviderIngestionExecutionItemSchema,
    DatabaseProviderIngestionExecutionListSchema,
    DatabaseProviderIngestionExecutionQuerySchema,
)
from ..services.database_provider_ingestion_execution_service import (
    DatabaseProviderIngestionExecutionService,
)
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(
    db: AsyncSession = Depends(get_session),
) -> DatabaseProviderIngestionExecutionService:
    return DatabaseProviderIngestionExecutionService(db)


@router.post(
    "/executions/",
    tags=["DatabaseProviderIngestionExecution"],
    response_model=DatabaseProviderIngestionExecutionItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_database_provider_ingestion_execution(
    database_provider_ingestion_execution_data: DatabaseProviderIngestionExecutionCreateSchema,
    service: DatabaseProviderIngestionExecutionService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
) -> DatabaseProviderIngestionExecutionItemSchema:
    """
    Adiciona uma instância da classe DatabaseProviderIngestionExecution.
    """
    result = await service.add(database_provider_ingestion_execution_data)
    await session.commit()
    return result


@router.delete(
    "/executions/{database_provider_ingestion_execution_id}",
    tags=["DatabaseProviderIngestionExecution"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_executions(
    database_provider_ingestion_execution_id: int = Path(
        ..., description="Identificador"
    ),
    service: DatabaseProviderIngestionExecutionService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
):
    """
    Exclui uma instância da classe DatabaseProviderIngestionExecution.
    """
    await service.delete(database_provider_ingestion_execution_id)
    await session.commit()
    return


@router.patch(
    "/executions/{database_provider_ingestion_execution_id}",
    tags=["DatabaseProviderIngestionExecution"],
    response_model=DatabaseProviderIngestionExecutionItemSchema,
    response_model_exclude_none=True,
)
async def update_executions(
    database_provider_ingestion_execution_id: int = Path(
        ..., description="Identificador"
    ),
    database_provider_ingestion_execution_data: typing.Optional[
        DatabaseProviderIngestionExecutionUpdateSchema
    ] = None,
    service: DatabaseProviderIngestionExecutionService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
) -> DatabaseProviderIngestionExecutionItemSchema:
    """
    Atualiza uma instância da classe DatabaseProviderIngestionExecution.
    """
    result = await service.update(
        database_provider_ingestion_execution_id,
        database_provider_ingestion_execution_data,
    )
    await session.commit()
    return result


@router.get(
    "/executions/",
    tags=["DatabaseProviderIngestionExecution"],
    response_model=PaginatedSchema[DatabaseProviderIngestionExecutionListSchema],
    response_model_exclude_none=True,
)
async def find_executions(
    query_options: DatabaseProviderIngestionExecutionQuerySchema = Depends(),
    service: DatabaseProviderIngestionExecutionService = Depends(_get_service),
) -> PaginatedSchema[DatabaseProviderIngestionExecutionListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    executions = await service.find(query_options)
    model = DatabaseProviderIngestionExecutionListSchema()
    executions.items = [model.model_validate(d) for d in executions.items]
    return executions


@router.get(
    "/executions/{database_provider_ingestion_execution_id}",
    tags=["DatabaseProviderIngestionExecution"],
    response_model=DatabaseProviderIngestionExecutionItemSchema,
    response_model_exclude_none=False,
)
async def get_database_provider_ingestion_execution(
    database_provider_ingestion_execution_id: int = Path(
        ..., description="Identificador"
    ),
    service: DatabaseProviderIngestionExecutionService = Depends(_get_service),
) -> DatabaseProviderIngestionExecutionItemSchema:
    """
    Recupera uma instância da classe DatabaseProviderIngestionExecution.
    """

    database_provider_ingestion_execution = await service.get(
        database_provider_ingestion_execution_id
    )
    if database_provider_ingestion_execution is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return database_provider_ingestion_execution
