#
import logging
import typing
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status

from ..schemas import (
    PaginatedSchema,
    DatabaseSchemaCreateSchema,
    DatabaseSchemaUpdateSchema,
    DatabaseSchemaItemSchema,
    DatabaseSchemaListSchema,
    DatabaseSchemaQuerySchema,
)
from ..services.database_schema_service import DatabaseSchemaService
from ..database import get_session
from ..routers import get_lookup_filter

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(
    db: AsyncSession = Depends(get_session),
) -> DatabaseSchemaService:
    return DatabaseSchemaService(db)


@router.post(
    "/schemas/",
    tags=["DatabaseSchema"],
    response_model=DatabaseSchemaItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_database_schema(
    database_schema_data: DatabaseSchemaCreateSchema,
    service: DatabaseSchemaService = Depends(_get_service),
) -> DatabaseSchemaItemSchema:
    """
    Adiciona uma instância da classe DatabaseSchema.
    """

    if database_schema_data is not None:
        database_schema_data.updated_by = "FIXME!!!"

    return await service.add(database_schema_data)


@router.delete(
    "/schemas/{entity_id}",
    tags=["DatabaseSchema"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_schemas(
    database_schema_id: typing.Union[UUID, str] = Depends(get_lookup_filter),
    service: DatabaseSchemaService = Depends(_get_service),
):
    """
    Exclui uma instância da classe DatabaseSchema.
    """
    await service.delete(database_schema_id)
    return


@router.patch(
    "/schemas/{entity_id}",
    tags=["DatabaseSchema"],
    response_model=DatabaseSchemaItemSchema,
    response_model_exclude_none=True,
)
async def update_schemas(
    database_schema_id: typing.Union[UUID, str] = Depends(get_lookup_filter),
    database_schema_data: typing.Optional[DatabaseSchemaUpdateSchema] = None,
    service: DatabaseSchemaService = Depends(_get_service),
) -> DatabaseSchemaItemSchema:
    """
    Atualiza uma instância da classe DatabaseSchema.
    """

    if database_schema_data is not None:
        database_schema_data.updated_by = "FIXME!!!"

    return await service.update(database_schema_id, database_schema_data)


@router.get(
    "/schemas/",
    tags=["DatabaseSchema"],
    response_model=PaginatedSchema[DatabaseSchemaListSchema],
    response_model_exclude_none=True,
)
async def find_schemas(
    query_options: DatabaseSchemaQuerySchema = Depends(),
    service: DatabaseSchemaService = Depends(_get_service),
) -> PaginatedSchema[DatabaseSchemaListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    schemas = await service.find(query_options)
    model = DatabaseSchemaListSchema()
    schemas.items = [model.model_validate(d) for d in schemas.items]
    return schemas


@router.get(
    "/schemas/{entity_id}",
    tags=["DatabaseSchema"],
    response_model=DatabaseSchemaItemSchema,
    response_model_exclude_none=False,
)
async def get_database_schema(
    database_schema_id: typing.Union[UUID, str] = Depends(get_lookup_filter),
    service: DatabaseSchemaService = Depends(_get_service),
) -> DatabaseSchemaItemSchema:
    """
    Recupera uma instância da classe DatabaseSchema.
    """

    database_schema = await service.get(database_schema_id)
    if database_schema is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return database_schema
