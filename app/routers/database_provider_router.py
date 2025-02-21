#
import json
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status, Path

from app.models import DatabaseProvider

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

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


@router.post(
    "/database-providers/",
    tags=["DatabaseProvider"],
    response_model=DatabaseProviderItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_database_provider(
    database_provider_data: DatabaseProviderCreateSchema,
    db: AsyncSession = Depends(get_session),
) -> DatabaseProviderItemSchema:
    """
    Adiciona uma instância da classe DatabaseProvider.
    """

    database_provider_data.updated_by = "FIXME!!!"

    return await DatabaseProviderService(db).add(database_provider_data)


@router.delete(
    "/database-providers/{database_provider_id}",
    tags=["DatabaseProvider"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_database_providers(
    database_provider_id: UUID, db: AsyncSession = Depends(get_session)
):
    """
    Exclui uma instância da classe DatabaseProvider.
    """
    await DatabaseProviderService(db).delete(database_provider_id)
    return


@router.patch(
    "/database-providers/{database_provider_id}",
    tags=["DatabaseProvider"],
    response_model=DatabaseProviderItemSchema,
    response_model_exclude_none=True,
)
async def update_database_providers(
    database_provider_id: UUID = Path(..., description="Identificador"),
    database_provider_data: DatabaseProviderUpdateSchema = None,
    db: AsyncSession = Depends(get_session),
) -> DatabaseProviderItemSchema:
    """
    Atualiza uma instância da classe DatabaseProvider.
    """

    database_provider_data.updated_by = "FIXME!!!"

    return await DatabaseProviderService(db).update(
        database_provider_id, database_provider_data
    )


@router.get(
    "/database-providers/",
    tags=["DatabaseProvider"],
    response_model=PaginatedSchema[DatabaseProviderListSchema],
    response_model_exclude_none=True,
)
async def find_database_providers(
    query_options: DatabaseProviderQuerySchema = Depends(),
    db: AsyncSession = Depends(get_session),
) -> PaginatedSchema[DatabaseProviderListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    database_providers = await DatabaseProviderService(db).find(query_options)
    model = DatabaseProviderListSchema()
    database_providers.items = [
        model.model_validate(d) for d in database_providers.items
    ]
    return database_providers


@router.get(
    "/database-providers/{database_provider_id}",
    tags=["DatabaseProvider"],
    response_model=DatabaseProviderItemSchema,
    response_model_exclude_none=False,
)
async def get_database_provider(
    database_provider_id: UUID = Path(..., description="Identificador"),
    db: AsyncSession = Depends(get_session),
) -> DatabaseProviderItemSchema:
    """
    Recupera uma instância da classe DatabaseProvider.
    """

    database_provider = await DatabaseProviderService(db).get(
        database_provider_id
    )
    if database_provider is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return database_provider

