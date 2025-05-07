import logging

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Request,
    Header
)
from typing import Optional
import base64
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

    try:
        # Base64 decode the JWT string from the header
        jwt_bytes = base64.b64decode(x_jwt_assertion)
        jwt_str = jwt_bytes.decode('utf-8')

        # Decode the JWT payload without verifying signature
        decoded_token = jwt.decode(jwt_str, options={"verify_signature": False})
        return {"decoded_jwt": decoded_token}

    except Exception as e:
        return {"error": str(e)}
