#
import logging
import typing
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status

from ..schemas import (
    PaginatedSchema,
    DatabaseProviderCreateSchema,
    DatabaseProviderUpdateSchema,
    DatabaseProviderItemSchema,
    DatabaseProviderListSchema,
    DatabaseProviderQuerySchema,
)
from ..services.database_provider_service import DatabaseProviderService
from ..database import get_session
from ..routers import get_lookup_filter

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(
    db: AsyncSession = Depends(get_session),
) -> DatabaseProviderService:
    return DatabaseProviderService(db)


@router.post(
    "/database-providers/",
    tags=["DatabaseProvider"],
    response_model=DatabaseProviderItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_database_provider(
    database_provider_data: DatabaseProviderCreateSchema,
    service: DatabaseProviderService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
) -> DatabaseProviderItemSchema:
    """
    Adiciona uma instância da classe DatabaseProvider.
    """

    if database_provider_data is not None:
        database_provider_data.updated_by = "FIXME!!!"
        base_fqn = "".join(
            char.lower() if char.isalnum() or char == "-" else ""
            for char in database_provider_data.name.replace(" ", "-")
        )
        fully_qualified_name = base_fqn
        counter = 1

        while await service.get(fully_qualified_name, silent=True):
            fully_qualified_name = f"{base_fqn}-{counter}"
            counter += 1

        database_provider_data.fully_qualified_name = fully_qualified_name

    result = await service.add(database_provider_data)
    await session.commit()
    return result


@router.delete(
    "/database-providers/{entity_id}",
    tags=["DatabaseProvider"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_database_providers(
    entity_id: typing.Union[UUID, str] = Depends(get_lookup_filter),
    service: DatabaseProviderService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
):
    """
    Exclui uma instância da classe DatabaseProvider.
    """
    await service.delete(entity_id)
    await session.commit()
    return


@router.patch(
    "/database-providers/{entity_id}",
    tags=["DatabaseProvider"],
    response_model=DatabaseProviderItemSchema,
    response_model_exclude_none=True,
)
async def update_database_providers(
    entity_id: typing.Union[UUID, str] = Depends(get_lookup_filter),
    database_provider_data: typing.Optional[DatabaseProviderUpdateSchema] = None,
    service: DatabaseProviderService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
) -> DatabaseProviderItemSchema:
    """
    Atualiza uma instância da classe DatabaseProvider.
    """

    if database_provider_data is not None:
        database_provider_data.updated_by = "FIXME!!!"

    result = await service.update(entity_id, database_provider_data)
    await session.commit()
    return result


@router.get(
    "/database-providers/",
    tags=["DatabaseProvider"],
    response_model=PaginatedSchema[DatabaseProviderListSchema],
    response_model_exclude_none=True,
)
async def find_database_providers(
    query_options: DatabaseProviderQuerySchema = Depends(),
    service: DatabaseProviderService = Depends(_get_service),
) -> PaginatedSchema[DatabaseProviderListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    database_providers = await service.find(query_options)
    model = DatabaseProviderListSchema()
    database_providers.items = [
        model.model_validate(d) for d in database_providers.items
    ]
    return database_providers


@router.get(
    "/database-providers/{entity_id}",
    tags=["DatabaseProvider"],
    response_model=DatabaseProviderItemSchema,
    response_model_exclude_none=False,
)
async def get_database_provider(
    entity_id: typing.Union[UUID, str] = Depends(get_lookup_filter),
    service: DatabaseProviderService = Depends(_get_service),
) -> DatabaseProviderItemSchema:
    """
    Recupera uma instância da classe DatabaseProvider.
    """

    database_provider = await service.get(entity_id)
    if database_provider is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return database_provider
