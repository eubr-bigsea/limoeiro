import json
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, Path, Response

from app.database import get_session
from app.models import DatabaseProviderIngestionExecution
from app.schemas import (
    DatabaseProviderIngestionExecutionItemSchema,
    DatabaseProviderIngestionItemSchema,
)
from pgqueuer import Queries
from fastapi import Request

router = APIRouter()

def get_pgq_queries(request: Request) -> Queries:
    """Retrieve Queries instance from FastAPI app context."""
    return request.app.extra["pgq_queries"]

@router.post(
    "/ingestions/start/{database_provider_ingestion_id}",
    tags=["DatabaseProviderIngestion"],
    response_model=DatabaseProviderIngestionItemSchema,
    response_model_exclude_none=False,
)
async def start_database_provider_ingestion(
    database_provider_ingestion_id: UUID = Path(
        ..., description="Identificador"
    ),
    session: AsyncSession = Depends(get_session),
    pgq_queries: Queries = Depends(get_pgq_queries),
) -> Response:
    """
    Inicia uma ingestão de dados
    """
    execution = DatabaseProviderIngestionExecution(
        status="preparing",
        trigger_mode="manual",
        triggered_by=None,  # FIXME
        ingestion_id=database_provider_ingestion_id,
    )
    session.add(execution)
    await session.flush()
    job_ids = await pgq_queries.enqueue(
        "start_ingestion",
        payload=json.dumps(
            {
                "ingestion": str(database_provider_ingestion_id),
                "execution": str(execution.id),
            }
        ).encode(),
    )
    execution.job_id = job_ids[0]
    session.add(execution)
    await session.commit()
    print("-" * 20)
    print(execution.id, execution)
    print("-" * 20)
    return Response(
        content=json.dumps({"status": "success", "execution_id": str(execution.id)}),
        status_code=200,
        media_type="application/json",
    )
