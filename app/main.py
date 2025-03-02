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
)
from fastapi.middleware.cors import CORSMiddleware
from .routers import domain_router
from dotenv import load_dotenv
from .utils.middlewares import add_middlewares
from sqlalchemy.exc import IntegrityError
from fastapi import Request

load_dotenv()

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
]
for router in routers:
    app.include_router(router)
