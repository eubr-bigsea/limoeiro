#
import logging
import typing
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status, Path

from ..schemas import (
    PaginatedSchema,
    ResponsibilityCreateSchema,
    ResponsibilityUpdateSchema,
    ResponsibilityItemSchema,
    ResponsibilityListSchema,
    ResponsibilityQuerySchema,
)
from ..services.responsibility_service import ResponsibilityService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(
    db: AsyncSession = Depends(get_session),
) -> ResponsibilityService:
    return ResponsibilityService(db)


@router.post(
    "/responsibilities/",
    tags=["Responsibility"],
    response_model=ResponsibilityItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_responsibility(
    responsibility_data: ResponsibilityCreateSchema,
    service: ResponsibilityService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
) -> ResponsibilityItemSchema:
    """
    Adiciona uma instância da classe Responsibility.
    """
    result = await service.add(responsibility_data)
    await session.commit()
    return result


@router.delete(
    "/responsibilities/{responsibility_id}",
    tags=["Responsibility"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_responsibilities(
    responsibility_id: None = Path(..., description=""),
    service: ResponsibilityService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
):
    """
    Exclui uma instância da classe Responsibility.
    """
    await service.delete(responsibility_id)
    await session.commit()
    return


@router.patch(
    "/responsibilities/{responsibility_id}",
    tags=["Responsibility"],
    response_model=ResponsibilityItemSchema,
    response_model_exclude_none=True,
)
async def update_responsibilities(
    responsibility_id: None = Path(..., description=""),
    responsibility_data: typing.Optional[ResponsibilityUpdateSchema] = None,
    service: ResponsibilityService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
) -> ResponsibilityItemSchema:
    """
    Atualiza uma instância da classe Responsibility.
    """
    result = await service.update(responsibility_id, responsibility_data)
    await session.commit()
    return result


@router.get(
    "/responsibilities/",
    tags=["Responsibility"],
    response_model=PaginatedSchema[ResponsibilityListSchema],
    response_model_exclude_none=True,
)
async def find_responsibilities(
    query_options: ResponsibilityQuerySchema = Depends(),
    service: ResponsibilityService = Depends(_get_service),
) -> PaginatedSchema[ResponsibilityListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    responsibilities = await service.find(query_options)
    model = ResponsibilityListSchema()
    responsibilities.items = [
        model.model_validate(d) for d in responsibilities.items
    ]
    return responsibilities


@router.get(
    "/responsibilities/{responsibility_id}",
    tags=["Responsibility"],
    response_model=ResponsibilityItemSchema,
    response_model_exclude_none=False,
)
async def get_responsibility(
    responsibility_id: None = Path(..., description=""),
    service: ResponsibilityService = Depends(_get_service),
) -> ResponsibilityItemSchema:
    """
    Recupera uma instância da classe Responsibility.
    """

    responsibility = await service.get(responsibility_id)
    if responsibility is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return responsibility
