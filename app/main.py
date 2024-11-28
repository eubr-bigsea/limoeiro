from fastapi import FastAPI

from app.routers import (
    database_provider_router,
    database_provider_type_router,
    database_router,
    database_schema_router,
    database_table_router
)
from fastapi.middleware.cors import CORSMiddleware
from .routers import domain_router
from dotenv import load_dotenv
from .utils.middlewares import add_middlewares


load_dotenv()

app = FastAPI()

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
# @app.exception_handler(AppExceptionCase)
# async def custom_app_exception_handler(request, e):
#     return await app_exception_handler(request, e)


routers = [
    domain_router.router,
    database_provider_type_router.router,
    database_provider_router.router,
    database_router.router,
    database_schema_router.router,
    database_table_router.router,
]
for router in routers:
    app.include_router(router)
