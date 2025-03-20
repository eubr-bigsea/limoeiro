#
import logging
import typing
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status, Path

from ..schemas import (
    PaginatedSchema,
    UserItemSchema,
    UserListSchema,
    UserCreateSchema,
    UserUpdateSchema,
    UserQuerySchema,
)
from ..services.user_service import UserService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(db: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(db)


@router.post(
    "/users/",
    tags=["User"],
    response_model=UserItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_user(
    user_data: UserCreateSchema, service: UserService = Depends(_get_service)
) -> UserItemSchema:
    """
    Adiciona uma instância da classe User.
    """
    return await service.add(user_data)


@router.delete(
    "/users/{user_id}", tags=["User"], status_code=status.HTTP_204_NO_CONTENT
)
async def delete_users(
    user_id: UUID = Path(..., description="Identificador"),
    service: UserService = Depends(_get_service),
):
    """
    Exclui uma instância da classe User.
    """
    await service.delete(user_id)
    return


@router.patch(
    "/users/{user_id}",
    tags=["User"],
    response_model=UserItemSchema,
    response_model_exclude_none=True,
)
async def update_users(
    user_id: UUID = Path(..., description="Identificador"),
    user_data: typing.Optional[UserUpdateSchema] = None,
    service: UserService = Depends(_get_service),
) -> UserItemSchema:
    """
    Atualiza uma instância da classe User.
    """
    return await service.update(user_id, user_data)


@router.get(
    "/users/",
    tags=["User"],
    response_model=PaginatedSchema[UserListSchema],
    response_model_exclude_none=True,
)
async def find_users(
    query_options: UserQuerySchema = Depends(),
    service: UserService = Depends(_get_service),
) -> PaginatedSchema[UserListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    users = await service.find(query_options)
    model = UserListSchema()
    users.items = [model.model_validate(d) for d in users.items]
    return users


@router.get(
    "/users/{user_id}",
    tags=["User"],
    response_model=UserItemSchema,
    response_model_exclude_none=False,
)
async def get_user(
    user_id: UUID = Path(..., description="Identificador"),
    service: UserService = Depends(_get_service),
) -> UserItemSchema:
    """
    Recupera uma instância da classe User.
    """

    user = await service.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return user
