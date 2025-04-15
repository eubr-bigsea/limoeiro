#
import logging
import typing
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status, Path

from ..schemas import (
    PaginatedSchema,
    RoleItemSchema,
    RoleListSchema,
    RoleCreateSchema,
    RoleUpdateSchema,
    RoleQuerySchema,
)
from ..services.role_service import RoleService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(db: AsyncSession = Depends(get_session)) -> RoleService:
    return RoleService(db)


@router.post(
    "/roles/",
    tags=["Role"],
    response_model=RoleItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_role(
    role_data: RoleCreateSchema,
    service: RoleService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
) -> RoleItemSchema:
    """
    Adiciona uma instância da classe Role.
    """
    result = await service.add(role_data)
    await session.commit()
    return result


@router.delete(
    "/roles/{role_id}", tags=["Role"], status_code=status.HTTP_204_NO_CONTENT
)
async def delete_roles(
    role_id: UUID = Path(..., description="Identificador"),
    service: RoleService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
):
    """
    Exclui uma instância da classe Role.
    """
    await service.delete(role_id)
    await session.commit()
    return


@router.patch(
    "/roles/{role_id}",
    tags=["Role"],
    response_model=RoleItemSchema,
    response_model_exclude_none=True,
)
async def update_roles(
    role_id: UUID = Path(..., description="Identificador"),
    role_data: typing.Optional[RoleUpdateSchema] = None,
    service: RoleService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
) -> RoleItemSchema:
    """
    Atualiza uma instância da classe Role.
    """
    result = await service.update(role_id, role_data)
    await session.commit()
    return result


@router.get(
    "/roles/",
    tags=["Role"],
    response_model=PaginatedSchema[RoleListSchema],
    response_model_exclude_none=True,
)
async def find_roles(
    query_options: RoleQuerySchema = Depends(),
    service: RoleService = Depends(_get_service),
) -> PaginatedSchema[RoleListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    roles = await service.find(query_options)
    model = RoleListSchema()
    roles.items = [model.model_validate(d) for d in roles.items]
    return roles


@router.get(
    "/roles/{role_id}",
    tags=["Role"],
    response_model=RoleItemSchema,
    response_model_exclude_none=False,
)
async def get_role(
    role_id: UUID = Path(..., description="Identificador"),
    service: RoleService = Depends(_get_service),
) -> RoleItemSchema:
    """
    Recupera uma instância da classe Role.
    """

    role = await service.get(role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return role
