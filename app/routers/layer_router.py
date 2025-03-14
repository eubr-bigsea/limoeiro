# 
import logging
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

@router.post("/layers/",
    tags=["Layer"],
    response_model=LayerItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True)
async def add_layer(
    layer_data: LayerCreateSchema,
    db: AsyncSession = Depends(get_session)) -> LayerItemSchema:
    """
    Adiciona uma instância da classe Layer.
    """
    return await LayerService(db).add(
        layer_data)

@router.delete("/layers/{layer_id}",
    tags=["Layer"],
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_layers(layer_id: UUID,
    db: AsyncSession = Depends(get_session)) :
    """
    Exclui uma instância da classe Layer.
    """
    await LayerService(db).delete(layer_id)
    return

@router.patch("/layers/{layer_id}",
    tags=["Layer"],
    response_model=LayerItemSchema,
    response_model_exclude_none=True)
async def update_layers(layer_id: UUID=Path(..., description="Identificador"),
    layer_data: LayerUpdateSchema=None,
    db: AsyncSession = Depends(get_session)) -> LayerItemSchema:
    """
    Atualiza uma instância da classe Layer.
    """
    return await LayerService(db).update(
        layer_id, layer_data)

@router.get(
    "/layers/",
    tags=["Layer"],
    response_model=PaginatedSchema[LayerListSchema],
    response_model_exclude_none=True
)
async def find_layers(
    query_options: LayerQuerySchema = Depends(),
    db: AsyncSession = Depends(get_session)
) -> PaginatedSchema[LayerListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    layers = await LayerService(db).find(query_options)
    model = LayerListSchema()
    layers.items = [model.model_validate(d) for d in layers.items]
    return layers

@router.get("/layers/{layer_id}",
    tags=["Layer"],
    response_model=LayerItemSchema,
    response_model_exclude_none=False)
async def get_layer(layer_id: UUID = Path(..., description="Identificador"),
    db: AsyncSession = Depends(get_session)) -> LayerItemSchema:
    """
    Recupera uma instância da classe Layer.
    """

    layer = await LayerService(db).get(
        layer_id)
    if layer is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return layer
