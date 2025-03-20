#
import logging
import typing
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status, Path

from ..schemas import (
    PaginatedSchema,
    DatabaseProviderConnectionCreateSchema,
    DatabaseProviderConnectionUpdateSchema,
    DatabaseProviderConnectionItemSchema,
    DatabaseProviderConnectionListSchema,
    DatabaseProviderConnectionQuerySchema,
)
from ..services.database_provider_connection_service import (
    DatabaseProviderConnectionService,
)
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(
    db: AsyncSession = Depends(get_session),
) -> DatabaseProviderConnectionService:
    return DatabaseProviderConnectionService(db)


@router.post(
    "/connections/",
    tags=["DatabaseProviderConnection"],
    response_model=DatabaseProviderConnectionItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_database_provider_connection(
    database_provider_connection_data: DatabaseProviderConnectionCreateSchema,
    service: DatabaseProviderConnectionService = Depends(_get_service),
) -> DatabaseProviderConnectionItemSchema:
    """
    Adiciona uma instância da classe DatabaseProviderConnection.
    """
    return await service.add(database_provider_connection_data)


@router.delete(
    "/connections/{entity_id}",
    tags=["DatabaseProviderConnection"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_connections(
    database_provider_connection_id: UUID = Path(
        ..., description="Identificador"
    ),
    service: DatabaseProviderConnectionService = Depends(_get_service),
):
    """
    Exclui uma instância da classe DatabaseProviderConnection.
    """
    await service.delete(database_provider_connection_id)
    return


@router.patch(
    "/connections/{entity_id}",
    tags=["DatabaseProviderConnection"],
    response_model=DatabaseProviderConnectionItemSchema,
    response_model_exclude_none=True,
)
async def update_connections(
    database_provider_connection_id: UUID = Path(
        ..., description="Identificador"
    ),
    database_provider_connection_data: typing.Optional[
        DatabaseProviderConnectionUpdateSchema
    ] = None,
    service: DatabaseProviderConnectionService = Depends(_get_service),
) -> DatabaseProviderConnectionItemSchema:
    """
    Atualiza uma instância da classe DatabaseProviderConnection.
    """
    return await service.update(
        database_provider_connection_id, database_provider_connection_data
    )


@router.get(
    "/connections/",
    tags=["DatabaseProviderConnection"],
    response_model=PaginatedSchema[DatabaseProviderConnectionListSchema],
    response_model_exclude_none=True,
)
async def find_connections(
    query_options: DatabaseProviderConnectionQuerySchema = Depends(),
    service: DatabaseProviderConnectionService = Depends(_get_service),
) -> PaginatedSchema[DatabaseProviderConnectionListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    connections = await service.find(query_options)
    model = DatabaseProviderConnectionListSchema()
    connections.items = [model.model_validate(d) for d in connections.items]
    return connections


@router.get(
    "/connections/{entity_id}",
    tags=["DatabaseProviderConnection"],
    response_model=DatabaseProviderConnectionItemSchema,
    response_model_exclude_none=False,
)
async def get_database_provider_connection(
    database_provider_connection_id: UUID = Path(
        ..., description="Identificador"
    ),
    service: DatabaseProviderConnectionService = Depends(_get_service),
) -> DatabaseProviderConnectionItemSchema:
    """
    Recupera uma instância da classe DatabaseProviderConnection.
    """

    database_provider_connection = await service.get(
        database_provider_connection_id
    )
    if database_provider_connection is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return database_provider_connection
