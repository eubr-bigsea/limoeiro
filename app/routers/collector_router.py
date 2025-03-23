import logging

from fastapi import (
    APIRouter,
    BackgroundTasks,
)

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
