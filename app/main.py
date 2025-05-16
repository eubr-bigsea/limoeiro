from contextlib import asynccontextmanager
import asyncio
import asyncpg
from apscheduler.schedulers.background import (
    BackgroundScheduler,
)  # runs tasks in the background
from apscheduler.triggers.cron import (
    CronTrigger,
)  # allows us to specify a recurring time for execution
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pgqueuer import AsyncpgDriver, Queries
from sqlalchemy.exc import IntegrityError

from app.collector.data_collection_scheduling_engine import DataCollectionSchedulingEngine
from app.database import DATABASE_URL
from app.exceptions import DatabaseException, EntityNotFoundException
from app.routers import (
    a_i_model_router,
    asset_router,
    collector_router,
    company_router,
    contact_router,
    database_provider_connection_router,
    database_provider_ingestion_execution_router,
    database_provider_ingestion_log_router,
    database_provider_ingestion_router,
    database_provider_ingestion_start_router,
    database_provider_router,
    database_provider_type_router,
    database_router,
    database_schema_router,
    database_table_router,
    database_table_sample_router,
    layer_router,
    permission_router,
    person_router,
    role_router,
    responsibility_type_router,
    tag_router,
    user_router,
)

from .routers import domain_router
from .utils.middlewares import add_middlewares
import urllib.parse
import os

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage async database connection throughout the app's lifespan."""
    # encode special characters from the password
    url_1 = DATABASE_URL.replace("+asyncpg", "").split("@")
    url_2 = url_1[0].split(":")
    password = url_2[2]
    password = urllib.parse.quote(password)
    dns = url_2[0]+":"+url_2[1]+":"+password+"@"+url_1[1]
    connection = await asyncpg.connect(dsn=dns)
    app.extra["pgq_queries"] = Queries(AsyncpgDriver(connection))  # type: ignore
    try:
        yield
    finally:
        await connection.close()


app = FastAPI(
    title="Limoeiro API",
    description="Documentação da API de catálogo de dados do Lemonade.",
    version="1.0.0",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    lifespan=lifespan,
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        license_info=app.license_info,
        description=app.description,
        routes=app.routes,
        openapi_version="3.0.2",  # Set your desired OpenAPI version here
    )

    # remover type: null
    def process_schema(schema):
        anyOf = schema.get("anyOf", {})
        if anyOf:
            for a in anyOf:
                if a.get("type") == "null":
                    anyOf.remove(a)
                    schema["nullable"] = True
                    break
        return schema

    for path in openapi_schema["paths"].values():
        for method in path.values():
            parameters = method.get("parameters", [])
            for p in parameters:
                schema = p.get("schema", {})
                process_schema(schema)

            requestBody = method.get("requestBody")
            if requestBody:
                content = requestBody.get("content")
                if content:
                    application_json = content.get("application/json")
                    schema = application_json.get("schema")
                    process_schema(schema)

    for component in openapi_schema["components"].values():
        for propertie in component.values():
            if propertie and propertie.get("properties"):
                for field in propertie.get("properties").values():
                    process_schema(field)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

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

ENABLE_SCHEDULER = eval(os.environ["ENABLE_SCHEDULER"])

# The task to run
def daily_task():
    pgq_queries = app.extra["pgq_queries"]
    engine = DataCollectionSchedulingEngine()
    asyncio.run(engine.execute_engine(pgq_queries))
    

    

if ENABLE_SCHEDULER == True:
    # Set up the scheduler
    scheduler = BackgroundScheduler()
    trigger = CronTrigger(hour=1, minute=0)
    scheduler.add_job(daily_task, trigger)
    scheduler.start()


routers = [
    a_i_model_router.router,
    asset_router.router,
    collector_router.router,
    company_router.router,
    contact_router.router,
    domain_router.router,
    database_provider_type_router.router,
    database_provider_router.router,
    database_provider_connection_router.router,
    database_provider_ingestion_router.router,
    database_provider_ingestion_execution_router.router,
    database_provider_ingestion_log_router.router,
    database_provider_ingestion_start_router.router,
    database_router.router,
    database_schema_router.router,
    database_table_router.router,
    database_table_sample_router.router,
    layer_router.router,
    permission_router.router,
    person_router.router,
    responsibility_type_router.router,
    role_router.router,
    tag_router.router,
    user_router.router,
]
for router in routers:
    app.include_router(router)
