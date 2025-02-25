#
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status, Path

from ..schemas import (
    PaginatedSchema,
    TagItemSchema,
    TagListSchema,
    TagCreateSchema,
    TagUpdateSchema,
    TagQuerySchema,
)
from ..services.tag_service import TagService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


@router.post(
    "/tags/",
    tags=["Tag"],
    response_model=TagItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_tag(
    tag_data: TagCreateSchema, db: AsyncSession = Depends(get_session)
) -> TagItemSchema:
    """
    Adiciona uma instância da classe Tag.
    """
    return await TagService(db).add(tag_data)


@router.delete(
    "/tags/{tag_id}", tags=["Tag"], status_code=status.HTTP_204_NO_CONTENT
)
async def delete_tags(tag_id: UUID, db: AsyncSession = Depends(get_session)):
    """
    Exclui uma instância da classe Tag.
    """
    await TagService(db).delete(tag_id)
    return


@router.patch(
    "/tags/{tag_id}",
    tags=["Tag"],
    response_model=TagItemSchema,
    response_model_exclude_none=True,
)
async def update_tags(
    tag_id: UUID = Path(..., description="Identificador"),
    tag_data: TagUpdateSchema = None,
    db: AsyncSession = Depends(get_session),
) -> TagItemSchema:
    """
    Atualiza uma instância da classe Tag.
    """
    return await TagService(db).update(tag_id, tag_data)


@router.get(
    "/tags/",
    tags=["Tag"],
    response_model=PaginatedSchema[TagListSchema],
    response_model_exclude_none=True,
)
async def find_tags(
    query_options: TagQuerySchema = Depends(),
    db: AsyncSession = Depends(get_session),
) -> PaginatedSchema[TagListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    tags = await TagService(db).find(query_options)
    model = TagListSchema()
    tags.items = [model.model_validate(d) for d in tags.items]
    return tags


@router.get(
    "/tags/{tag_id}",
    tags=["Tag"],
    response_model=TagItemSchema,
    response_model_exclude_none=False,
)
async def get_tag(
    tag_id: UUID = Path(..., description="Identificador"),
    db: AsyncSession = Depends(get_session),
) -> TagItemSchema:
    """
    Recupera uma instância da classe Tag.
    """

    tag = await TagService(db).get(tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return tag
