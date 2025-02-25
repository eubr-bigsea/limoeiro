#
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, Path

from ..schemas import (
    BaseQuerySchema,
    PaginatedSchema,
    DatabaseProviderTypeItemSchema,
    DatabaseProviderTypeListSchema,
)
from ..services.database_provider_type_service import DatabaseProviderTypeService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


@router.get(
    "/database-provider-types/{database_provider_type_id}",
    tags=["DatabaseProviderType"],
    response_model=DatabaseProviderTypeItemSchema,
    response_model_exclude_none=False,
)
async def get_database_provider_type(
    database_provider_type_id: str = Path(..., description="Identicador"),
    db: AsyncSession = Depends(get_session),
) -> DatabaseProviderTypeItemSchema:
    """
    Recupera uma instância da classe DatabaseProviderType.
    """

    database_provider_type = await DatabaseProviderTypeService(db).get(
        database_provider_type_id
    )
    if database_provider_type is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return database_provider_type


@router.get(
    "/database-provider-types/",
    tags=["DatabaseProviderType"],
    response_model=PaginatedSchema[DatabaseProviderTypeListSchema],
    response_model_exclude_none=True,
)
async def find_database_provider_types(
    query_options: BaseQuerySchema = Depends(),
    db: AsyncSession = Depends(get_session),
) -> PaginatedSchema[DatabaseProviderTypeListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    database_provider_types = await DatabaseProviderTypeService(db).find(
        query_options
    )
    model = DatabaseProviderTypeListSchema()
    database_provider_types.items = [
        model.model_validate(d) for d in database_provider_types.items
    ]
    return database_provider_types
