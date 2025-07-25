#
import logging
import typing
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status

from ..schemas import (
    PaginatedSchema,
    DatabaseCreateSchema,
    DatabaseUpdateSchema,
    DatabaseItemSchema,
    DatabaseListSchema,
    DatabaseQuerySchema,
)
from ..services.database_service import DatabaseService
from ..database import get_session
from ..routers import get_lookup_filter

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(db: AsyncSession = Depends(get_session)) -> DatabaseService:
    return DatabaseService(db)


@router.post(
    "/databases/",
    tags=["Database"],
    response_model=DatabaseItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_database(
    database_data: DatabaseCreateSchema,
    service: DatabaseService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
) -> DatabaseItemSchema:
    """
    Adiciona uma instância da classe Database.
    """

    if database_data is not None:
        database_data.updated_by = "FIXME!!!"

    result = await service.add(database_data)
    await session.commit()
    return result


@router.delete(
    "/databases/{entity_id}",
    tags=["Database"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_databases(
    entity_id: typing.Union[UUID, str] = Depends(get_lookup_filter),
    service: DatabaseService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
):
    """
    Exclui uma instância da classe Database.
    """
    await service.delete(entity_id)
    await session.commit()
    return


@router.patch(
    "/databases/{entity_id}",
    tags=["Database"],
    response_model=DatabaseItemSchema,
    response_model_exclude_none=True,
)
async def update_databases(
    entity_id: typing.Union[UUID, str] = Depends(get_lookup_filter),
    database_data: typing.Optional[DatabaseUpdateSchema] = None,
    service: DatabaseService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
) -> DatabaseItemSchema:
    """
    Atualiza uma instância da classe Database.
    """

    if database_data is not None:
        database_data.updated_by = "FIXME!!!"

    result = await service.update(entity_id, database_data)
    await session.commit()
    return result


@router.get(
    "/databases/",
    tags=["Database"],
    response_model=PaginatedSchema[DatabaseListSchema],
    response_model_exclude_none=True,
)
async def find_databases(
    query_options: DatabaseQuerySchema = Depends(),
    service: DatabaseService = Depends(_get_service),
) -> PaginatedSchema[DatabaseListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    databases = await service.find(query_options)
    model = DatabaseListSchema()
    databases.items = [model.model_validate(d) for d in databases.items]
    return databases


@router.get(
    "/databases/{entity_id}",
    tags=["Database"],
    response_model=DatabaseItemSchema,
    response_model_exclude_none=False,
)
async def get_database(
    entity_id: typing.Union[UUID, str] = Depends(get_lookup_filter),
    service: DatabaseService = Depends(_get_service),
) -> DatabaseItemSchema:
    """
    Recupera uma instância da classe Database.
    """

    database = await service.get(entity_id)
    if database is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return database
