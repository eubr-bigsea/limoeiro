#
import logging
import typing
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status, Path

from ..schemas import (
    PaginatedSchema,
    LayerCreateSchema,
    LayerUpdateSchema,
    LayerItemSchema,
    LayerListSchema,
    LayerQuerySchema,
)
from ..services.layer_service import LayerService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(db: AsyncSession = Depends(get_session)) -> LayerService:
    return LayerService(db)


@router.post(
    "/layers/",
    tags=["Layer"],
    response_model=LayerItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_layer(
    layer_data: LayerCreateSchema, service: LayerService = Depends(_get_service)
) -> LayerItemSchema:
    """
    Adiciona uma instância da classe Layer.
    """
    return await service.add(layer_data)


@router.delete(
    "/layers/{layer_id}", tags=["Layer"], status_code=status.HTTP_204_NO_CONTENT
)
async def delete_layers(
    layer_id: UUID, service: LayerService = Depends(_get_service)
):
    """
    Exclui uma instância da classe Layer.
    """
    await service.delete(layer_id)
    return


@router.patch(
    "/layers/{layer_id}",
    tags=["Layer"],
    response_model=LayerItemSchema,
    response_model_exclude_none=True,
)
async def update_layers(
    layer_id: UUID = Path(..., description="Identificador"),
    layer_data: typing.Optional[LayerUpdateSchema] = None,
    service: LayerService = Depends(_get_service),
) -> LayerItemSchema:
    """
    Atualiza uma instância da classe Layer.
    """
    return await service.update(layer_id, layer_data)


@router.get(
    "/layers/",
    tags=["Layer"],
    response_model=PaginatedSchema[LayerListSchema],
    response_model_exclude_none=True,
)
async def find_layers(
    query_options: LayerQuerySchema = Depends(),
    service: LayerService = Depends(_get_service),
) -> PaginatedSchema[LayerListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    layers = await service.find(query_options)
    model = LayerListSchema()
    layers.items = [model.model_validate(d) for d in layers.items]
    return layers


@router.get(
    "/layers/{layer_id}",
    tags=["Layer"],
    response_model=LayerItemSchema,
    response_model_exclude_none=False,
)
async def get_layer(
    layer_id: UUID = Path(..., description="Identificador"),
    service: LayerService = Depends(_get_service),
) -> LayerItemSchema:
    """
    Recupera uma instância da classe Layer.
    """

    layer = await service.get(layer_id)
    if layer is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return layer
