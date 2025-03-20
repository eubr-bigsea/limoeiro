#
import logging
import typing
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status, Path

from ..schemas import (
    PaginatedSchema,
    AIModelCreateSchema,
    AIModelUpdateSchema,
    AIModelItemSchema,
    AIModelListSchema,
    AIModelQuerySchema,
)
from ..services.a_i_model_service import AIModelService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(db: AsyncSession = Depends(get_session)) -> AIModelService:
    return AIModelService(db)


@router.post(
    "/ai-models/",
    tags=["AIModel"],
    response_model=AIModelItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_a_i_model(
    a_i_model_data: AIModelCreateSchema,
    service: AIModelService = Depends(_get_service),
) -> AIModelItemSchema:
    """
    Adiciona uma instância da classe AIModel.
    """

    if a_i_model_data is not None:
        a_i_model_data.updated_by = "FIXME!!!"

    return await service.add(a_i_model_data)


@router.delete(
    "/ai-models/{entity_id}",
    tags=["AIModel"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_ai_models(
    a_i_model_id: UUID = Path(..., description="Identificador"),
    service: AIModelService = Depends(_get_service),
):
    """
    Exclui uma instância da classe AIModel.
    """
    await service.delete(a_i_model_id)
    return


@router.patch(
    "/ai-models/{entity_id}",
    tags=["AIModel"],
    response_model=AIModelItemSchema,
    response_model_exclude_none=True,
)
async def update_ai_models(
    a_i_model_id: UUID = Path(..., description="Identificador"),
    a_i_model_data: typing.Optional[AIModelUpdateSchema] = None,
    service: AIModelService = Depends(_get_service),
) -> AIModelItemSchema:
    """
    Atualiza uma instância da classe AIModel.
    """

    if a_i_model_data is not None:
        a_i_model_data.updated_by = "FIXME!!!"

    return await service.update(a_i_model_id, a_i_model_data)


@router.get(
    "/ai-models/",
    tags=["AIModel"],
    response_model=PaginatedSchema[AIModelListSchema],
    response_model_exclude_none=True,
)
async def find_ai_models(
    query_options: AIModelQuerySchema = Depends(),
    service: AIModelService = Depends(_get_service),
) -> PaginatedSchema[AIModelListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    ai_models = await service.find(query_options)
    model = AIModelListSchema()
    ai_models.items = [model.model_validate(d) for d in ai_models.items]
    return ai_models


@router.get(
    "/ai-models/{entity_id}",
    tags=["AIModel"],
    response_model=AIModelItemSchema,
    response_model_exclude_none=False,
)
async def get_a_i_model(
    a_i_model_id: UUID = Path(..., description="Identificador"),
    service: AIModelService = Depends(_get_service),
) -> AIModelItemSchema:
    """
    Recupera uma instância da classe AIModel.
    """

    a_i_model = await service.get(a_i_model_id)
    if a_i_model is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return a_i_model
