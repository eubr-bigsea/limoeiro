#
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, Path

from ..schemas import (
    BaseQuerySchema,
    PaginatedSchema,
    ResponsibilityTypeItemSchema,
    ResponsibilityTypeListSchema,
)
from ..services.responsibility_type_service import ResponsibilityTypeService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(
    db: AsyncSession = Depends(get_session),
) -> ResponsibilityTypeService:
    return ResponsibilityTypeService(db)


@router.get(
    "/responsibility-types/{entity_id}",
    tags=["ResponsibilityType"],
    response_model=ResponsibilityTypeItemSchema,
    response_model_exclude_none=False,
)
async def get_responsibility_type(
    responsibility_type_id: UUID = Path(..., description="Identificador"),
    service: ResponsibilityTypeService = Depends(_get_service),
) -> ResponsibilityTypeItemSchema:
    """
    Recupera uma instância da classe ResponsibilityType.
    """

    responsibility_type = await service.get(responsibility_type_id)
    if responsibility_type is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return responsibility_type


@router.get(
    "/responsibility-types/",
    tags=["ResponsibilityType"],
    response_model=PaginatedSchema[ResponsibilityTypeListSchema],
    response_model_exclude_none=True,
)
async def find_responsibility_types(
    query_options: BaseQuerySchema = Depends(),
    service: ResponsibilityTypeService = Depends(_get_service),
) -> PaginatedSchema[ResponsibilityTypeListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    responsibility_types = await service.find(query_options)
    model = ResponsibilityTypeListSchema()
    responsibility_types.items = [
        model.model_validate(d) for d in responsibility_types.items
    ]
    return responsibility_types
