#
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from ..schemas import (
    PaginatedSchema,
    DatabaseProviderIngestionLogListSchema,
    DatabaseProviderIngestionLogQuerySchema,
)
from ..services.database_provider_ingestion_log_service import (
    DatabaseProviderIngestionLogService,
)
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(
    db: AsyncSession = Depends(get_session),
) -> DatabaseProviderIngestionLogService:
    return DatabaseProviderIngestionLogService(db)


@router.get(
    "/ingestion-logs/",
    tags=["DatabaseProviderIngestionLog"],
    response_model=PaginatedSchema[DatabaseProviderIngestionLogListSchema],
    response_model_exclude_none=True,
)
async def find_ingestion_logs(
    query_options: DatabaseProviderIngestionLogQuerySchema = Depends(),
    service: DatabaseProviderIngestionLogService = Depends(_get_service),
) -> PaginatedSchema[DatabaseProviderIngestionLogListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    ingestion_logs = await service.find(query_options)
    model = DatabaseProviderIngestionLogListSchema()
    ingestion_logs.items = [
        model.model_validate(d) for d in ingestion_logs.items
    ]
    return ingestion_logs
