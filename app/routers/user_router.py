#
import base64
import json
import logging
import typing
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, Header, status, Path

from app.models import (
    Permission,
    Role,
    User,
    role_permission,
    user_role
)

from ..schemas import (
    PaginatedSchema,
    PermissionItemSchema,
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
    user_data: UserCreateSchema,
    service: UserService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
) -> UserItemSchema:
    """
    Adiciona uma instância da classe User.
    """
    result = await service.add(user_data)
    await session.commit()
    return result


@router.delete(
    "/users/{user_id}", tags=["User"], status_code=status.HTTP_204_NO_CONTENT
)
async def delete_users(
    user_id: UUID = Path(..., description="Identificador"),
    service: UserService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
):
    """
    Exclui uma instância da classe User.
    """
    await service.delete(user_id)
    await session.commit()
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
    session: AsyncSession = Depends(get_session),
) -> UserItemSchema:
    """
    Atualiza uma instância da classe User.
    """
    result = await service.update(user_id, user_data)
    await session.commit()
    return result


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

@router.get(
    "/users/permissions/",
    tags=["User"],
    response_model=typing.List[PermissionItemSchema],
    response_model_exclude_none=False
)
async def get_user_permissions(
    x_jwt_assertion: typing.Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
) -> typing.List[PermissionItemSchema]:
    """
    Recupera uma lista de permissões que o usuário passado pelo jwt_token possui.
    """
    if not x_jwt_assertion:
        return {"error": "X-JWT-Assertion header missing"}

    _, payload, _ = x_jwt_assertion.split('.')
    padded = payload + '=' * (-len(payload) % 4)
    try:
        payload_decoded = base64.urlsafe_b64decode(padded)
        payload_decoded = json.loads(payload_decoded)
        username = payload_decoded['scope']
        sql = (
            select(Permission).distinct()
            .join(role_permission, Permission.id == role_permission.c.tb_permission_id)
            .join(Role, role_permission.c.role_id == Role.id)
            .join(user_role, Role.id == user_role.c.role_id)
            .join(User, user_role.c.tb_user_id == User.id)
            .where(User.login == username)
        )
        permissions = (await session.execute(sql)).scalars().all()
        return [PermissionItemSchema.model_validate(permission) for permission in list(permissions)]
    except Exception as e:
        return {"error": str(e)}