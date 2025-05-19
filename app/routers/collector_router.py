import logging
import asyncio
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Request,
    Header,
    Depends
)
from typing import Optional
import base64
import json
import jwt
from pgqueuer import Queries
from fastapi import Request
from app.collector.data_collection_scheduling_engine import DataCollectionSchedulingEngine

router = APIRouter()
log = logging.getLogger(__name__)


def get_pgq_queries(request: Request) -> Queries:
    """Retrieve Queries instance from FastAPI app context."""
    return request.app.extra["pgq_queries"]

def run_engine(pgq_queries):
    engine = DataCollectionSchedulingEngine()
    asyncio.run(engine.execute_engine(pgq_queries))

@router.post("/collector/", tags=["Collector"])
async def collect_data(
    background_tasks: BackgroundTasks,
    pgq_queries: Queries = Depends(get_pgq_queries),
):
    if background_tasks is not None:     
        background_tasks.add_task(run_engine, pgq_queries)
    return True


@router.get("/collector/secure-endpoint", tags=["Collector"])
async def secure_endpoint(request: Request, x_jwt_assertion: Optional[str] = Header(None)):
    if not x_jwt_assertion:
        return {"error": "X-JWT-Assertion header missing"}

    header, payload, signature = x_jwt_assertion.split('.')
    padded = payload + '=' * (-len(payload) % 4)
    try:
        payload_decoded = base64.urlsafe_b64decode(padded)
        payload_decoded = json.loads(payload_decoded)
        return payload_decoded
    except Exception as e:
        return {"error": str(e)}
    
