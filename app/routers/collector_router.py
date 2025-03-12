
import logging
from fastapi import APIRouter, HTTPException, Depends, status, Path, BackgroundTasks


from ..database import get_session
from app.collector.data_collection_engine import DataCollectionEngine

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*

@router.post("/collector/",
    tags=["Collector"]

)
async def collect_data (background_tasks: BackgroundTasks = None):
    engine = DataCollectionEngine()
    background_tasks.add_task(engine.execute_engine)
    return True

