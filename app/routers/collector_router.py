import logging

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Request,
    Header
)
from typing import Optional
import base64
import json
import jwt
from app.collector.data_collection_engine import DataCollectionEngine

router = APIRouter()
log = logging.getLogger(__name__)


@router.post("/collector/", tags=["Collector"])
async def collect_data(
    background_tasks: BackgroundTasks,
):
    engine = DataCollectionEngine()
    if background_tasks is not None:
        background_tasks.add_task(engine.execute_engine)
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
    
