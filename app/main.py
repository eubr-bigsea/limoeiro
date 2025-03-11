from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.exceptions import DatabaseException
from app.routers import (
    database_provider_router,
    database_provider_type_router,
    database_provider_connection_router,
    database_provider_ingestion_router,
    database_router,
    database_schema_router,
    database_table_router,
    layer_router,
    tag_router,
    collector_router,
)
from fastapi.middleware.cors import CORSMiddleware
from .routers import domain_router
from dotenv import load_dotenv
from .utils.middlewares import add_middlewares
from sqlalchemy.exc import IntegrityError
from fastapi import Request

from apscheduler.schedulers.background import BackgroundScheduler  # runs tasks in the background
from apscheduler.triggers.cron import CronTrigger  # allows us to specify a recurring time for execution
from app.collector.data_collection_engine import DataCollectionEngine

load_dotenv()

# The task to run
def daily_task():
    DataCollectionEngine().execute_engine()

# Set up the scheduler
scheduler = BackgroundScheduler()
trigger = CronTrigger(hour=1, minute=0)
scheduler.add_job(daily_task, trigger)
scheduler.start()


app = FastAPI(
    title="Limoeiro API",
    description="Documentação da API de catálogo de dados do Lemonade.",
    version="1.0.0",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        }
)

print("Adding CORS")
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    #allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
add_middlewares(app)

@app.exception_handler(DatabaseException)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Global handler for PostgreSQL IntegrityError."""
    detail = str(exc)
    return JSONResponse(
        status_code=400,
        content={"error": detail}
    )


routers = [
    domain_router.router,
    database_provider_type_router.router,
    database_provider_router.router,
    database_provider_connection_router.router,
    database_provider_ingestion_router.router,
    database_router.router,
    database_schema_router.router,
    database_table_router.router,
    layer_router.router,
    tag_router.router,
    collector_router.router,
]
for router in routers:
    app.include_router(router)
