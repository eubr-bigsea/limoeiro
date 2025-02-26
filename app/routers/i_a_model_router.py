#
import logging
import typing
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status, Path

from ..schemas import (
    PaginatedSchema,
    IAModelCreateSchema,
    IAModelUpdateSchema,
    IAModelItemSchema,
    IAModelListSchema,
    IAModelQuerySchema,
)
from ..services.i_a_model_service import IAModelService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(db: AsyncSession = Depends(get_session)) -> IAModelService:
    return IAModelService(db)


@router.post(
    "/ia-models/",
    tags=["IAModel"],
    response_model=IAModelItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_i_a_model(
    i_a_model_data: IAModelCreateSchema,
    service: IAModelService = Depends(_get_service),
) -> IAModelItemSchema:
    """
    Adiciona uma instância da classe IAModel.
    """

    if i_a_model_data is not None:
        i_a_model_data.updated_by = "FIXME!!!"

    return await service.add(i_a_model_data)


@router.delete(
    "/ia-models/{i_a_model_id}",
    tags=["IAModel"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_ia_models(
    i_a_model_id: UUID, service: IAModelService = Depends(_get_service)
):
    """
    Exclui uma instância da classe IAModel.
    """
    await service.delete(i_a_model_id)
    return


@router.patch(
    "/ia-models/{i_a_model_id}",
    tags=["IAModel"],
    response_model=IAModelItemSchema,
    response_model_exclude_none=True,
)
async def update_ia_models(
    i_a_model_id: UUID = Path(..., description="Identificador"),
    i_a_model_data: typing.Optional[IAModelUpdateSchema] = None,
    service: IAModelService = Depends(_get_service),
) -> IAModelItemSchema:
    """
    Atualiza uma instância da classe IAModel.
    """

    if i_a_model_data is not None:
        i_a_model_data.updated_by = "FIXME!!!"

    return await service.update(i_a_model_id, i_a_model_data)


@router.get(
    "/ia-models/",
    tags=["IAModel"],
    response_model=PaginatedSchema[IAModelListSchema],
    response_model_exclude_none=True,
)
async def find_ia_models(
    query_options: IAModelQuerySchema = Depends(),
    service: IAModelService = Depends(_get_service),
) -> PaginatedSchema[IAModelListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    ia_models = await service.find(query_options)
    model = IAModelListSchema()
    ia_models.items = [model.model_validate(d) for d in ia_models.items]
    return ia_models


@router.get(
    "/ia-models/{i_a_model_id}",
    tags=["IAModel"],
    response_model=IAModelItemSchema,
    response_model_exclude_none=False,
)
async def get_i_a_model(
    i_a_model_id: UUID = Path(..., description="Identificador"),
    service: IAModelService = Depends(_get_service),
) -> IAModelItemSchema:
    """
    Recupera uma instância da classe IAModel.
    """

    i_a_model = await service.get(i_a_model_id)
    if i_a_model is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return i_a_model
