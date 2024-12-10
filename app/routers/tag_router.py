import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends

from ..schemas import (
    BaseQuerySchema,
    PaginatedSchema,
    TagItemSchema,
    TagListSchema,
)
from ..services.tag_service import TagService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*

@router.get("/tags/{tag_id}",
    tags=["Tag"],
    response_model=TagItemSchema,
    response_model_exclude_none=False)
async def get_tag(tag_id: UUID,
    db: AsyncSession = Depends(get_session)) -> TagItemSchema:
    """
    Retrieve a single instance of class Tag.

    :param tag_id: The ID of the instance to retrieve.
    :type tag_id: int
    :return: A JSON object containing the Tag instance data.
    :rtype: dict
    """

    tag = await TagService(db).get(
        tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return tag

@router.get(
    "/tags/",
    tags=["Tag"],
    response_model=PaginatedSchema[TagListSchema],
    response_model_exclude_none=True
)
async def find_tags(
    query_options: BaseQuerySchema = Depends(),
    db: AsyncSession = Depends(get_session)
) -> PaginatedSchema[TagListSchema]:
    """
    Retrieve a list of instances using query options.
    :param query_options: Query options for sorting, filtering and paging.
    :return: A JSON object containing the list of instances data.
    :rtype: dict
    """
    tags = await TagService(db).find(query_options)
    model = TagListSchema()
    tags.items = [model.model_validate(d) for d in tags.items]
    return tags
