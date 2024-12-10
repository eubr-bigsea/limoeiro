import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status

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

@router.post("/ia-models/",
    tags=["IAModel"],
    response_model=IAModelItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True)
async def add_i_a_model(
    i_a_model_data: IAModelCreateSchema,
    db: AsyncSession = Depends(get_session)) -> IAModelItemSchema:
    """
    Add a single instance of class IAModel.

    :return: A JSON object containing a success message.
    :rtype: dict
    """
        
    i_a_model_data.updated_by = "FIXME!!!"

    return await IAModelService(db).add(
        i_a_model_data)

@router.delete("/ia-models/{i_a_model_id}",
    tags=["IAModel"],
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_ia_models(i_a_model_id: UUID,
    db: AsyncSession = Depends(get_session)) :
    """
    Delete a single instance of class IAModel.

    :param i_a_model_id: The ID of the instance to delete.
    :type i_a_model_id: int
    :return: A JSON object containing a success message.
    :rtype: dict
    """
    await IAModelService(db).delete(i_a_model_id)
    return

@router.patch("/ia-models/{i_a_model_id}",
    tags=["IAModel"],
    response_model=IAModelItemSchema,
    response_model_exclude_none=True)
async def update_ia_models(i_a_model_id: UUID,
    i_a_model_data: IAModelUpdateSchema,
    db: AsyncSession = Depends(get_session)) -> IAModelItemSchema:
    """
    Update a single instance of class IAModel.

    :param i_a_model_id: The ID of the instance to update.
    :type i_a_model_id: int
    :return: A JSON object containing a success message.
    :rtype: dict
    """
        
    i_a_model_data.updated_by = "FIXME!!!"

    return await IAModelService(db).update(
        i_a_model_id, i_a_model_data)

@router.get(
    "/ia-models/",
    tags=["IAModel"],
    response_model=PaginatedSchema[IAModelListSchema],
    response_model_exclude_none=True
)
async def find_ia_models(
    query_options: IAModelQuerySchema = Depends(),
    db: AsyncSession = Depends(get_session)
) -> PaginatedSchema[IAModelListSchema]:
    """
    Retrieve a list of instances using query options.
    :param query_options: Query options for sorting, filtering and paging.
    :return: A JSON object containing the list of instances data.
    :rtype: dict
    """
    ia_models = await IAModelService(db).find(query_options)
    model = IAModelListSchema()
    ia_models.items = [model.model_validate(d) for d in ia_models.items]
    return ia_models

@router.get("/ia-models/{i_a_model_id}",
    tags=["IAModel"],
    response_model=IAModelItemSchema,
    response_model_exclude_none=False)
async def get_i_a_model(i_a_model_id: UUID,
    db: AsyncSession = Depends(get_session)) -> IAModelItemSchema:
    """
    Retrieve a single instance of class IAModel.

    :param i_a_model_id: The ID of the instance to retrieve.
    :type i_a_model_id: int
    :return: A JSON object containing the IAModel instance data.
    :rtype: dict
    """

    i_a_model = await IAModelService(db).get(
        i_a_model_id)
    if i_a_model is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return i_a_model
