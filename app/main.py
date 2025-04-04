from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions import DatabaseException, EntityNotFoundException
from app.routers import (
    asset_router,
    collector_router,
    company_router,
    contact_router,
    database_provider_router,
    database_provider_type_router,
    database_provider_connection_router,
    database_provider_ingestion_router,
    database_router,
    database_schema_router,
    database_table_router,
    database_table_sample_router,
    layer_router,
    person_router,
    responsibility_type_router,
    tag_router,
    user_router,
)
from fastapi.middleware.cors import CORSMiddleware
from .routers import domain_router
from dotenv import load_dotenv
from .utils.middlewares import add_middlewares
from sqlalchemy.exc import IntegrityError
from fastapi import Request

from apscheduler.schedulers.background import (
    BackgroundScheduler,
)  # runs tasks in the background
from apscheduler.triggers.cron import (
    CronTrigger,
)  # allows us to specify a recurring time for execution
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
    },
)
app.openapi_version = "3.0.2"
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
add_middlewares(app)


@app.exception_handler(DatabaseException)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Global handler for PostgreSQL IntegrityError."""
    detail = str(exc)
    return JSONResponse(status_code=400, content={"error": detail})


@app.exception_handler(EntityNotFoundException)
async def not_found_exception_handler(
    request: Request, exc: EntityNotFoundException
):
    """Global handler for PostgreSQL IntegrityError."""
    detail = str(exc)
    return JSONResponse(status_code=404, content={"error": detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    # logger.error(request, exc_str)
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


routers = [
    asset_router.router,
    collector_router.router,
    company_router.router,
    contact_router.router,
    domain_router.router,
    database_provider_type_router.router,
    database_provider_router.router,
    database_provider_connection_router.router,
    database_provider_ingestion_router.router,
    database_router.router,
    database_schema_router.router,
    database_table_router.router,
    database_table_sample_router.router,
    layer_router.router,
    person_router.router,
    tag_router.router,
    responsibility_type_router.router,
    user_router.router,
]
for router in routers:
    app.include_router(router)
