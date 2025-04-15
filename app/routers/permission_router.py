#
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from ..schemas import (
    BaseQuerySchema,
    PaginatedSchema,
    PermissionListSchema,
)
from ..services.permission_service import PermissionService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(db: AsyncSession = Depends(get_session)) -> PermissionService:
    return PermissionService(db)


@router.get(
    "/permissions/",
    tags=["Permission"],
    response_model=PaginatedSchema[PermissionListSchema],
    response_model_exclude_none=True,
)
async def find_permissions(
    query_options: BaseQuerySchema = Depends(),
    service: PermissionService = Depends(_get_service),
) -> PaginatedSchema[PermissionListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    permissions = await service.find(query_options)
    model = PermissionListSchema()
    permissions.items = [model.model_validate(d) for d in permissions.items]
    return permissions
