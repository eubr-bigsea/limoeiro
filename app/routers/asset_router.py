#
import logging
import typing
from uuid import UUID
from sqlalchemy import select, delete, update
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Path

from app.models import AssetLink, AssetTag, Responsibility, Tag

from ..schemas import (
    AssetLinkCreateSchema,
    ResponsibilityCreateSchema,
    ResponsibilityItemSchema,
    TagItemSchema,
    AssetLinkItemSchema,
)
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)


@router.get(
    "/assets/tags/{asset_id}",
    tags=["Asset"],
    response_model=typing.List[TagItemSchema],
    response_model_exclude_none=False,
)
async def get_tags(
    asset_id: UUID = Path(..., description="Identificador"),
    session: AsyncSession = Depends(get_session),
) -> typing.List[TagItemSchema]:
    """
    Recupera tags associadas ao ativo
    """
    sql = (
        select(Tag)
        .join(AssetTag)
        .filter(AssetTag.asset_id == asset_id)
        .order_by(Tag.name)
    )
    rows = (await session.execute(sql)).scalars().all()
    print([row.name for row in list(rows)])
    return [TagItemSchema.model_validate(row) for row in list(rows)]


@router.delete("/assets/tags/{asset_id}/{tag_id}", tags=["Asset"])
async def delete_tag(
    asset_id: UUID = Path(..., description="Identificador do ativo"),
    tag_id: UUID = Path(..., description="Identificador da tag"),
    session: AsyncSession = Depends(get_session),
):
    """
    Exclui uma tag associada ao ativo
    """
    await session.execute(
        delete(AssetTag)
        .where(AssetTag.asset_id == asset_id)
        .where(AssetTag.tag_id == tag_id)
    )
    await session.commit()


@router.post("/assets/tags/{asset_id}/{tag_id}", tags=["Asset"])
async def add_tag(
    asset_id: UUID = Path(..., description="Identificador do ativo"),
    tag_id: UUID = Path(..., description="Identificador da tag"),
    session: AsyncSession = Depends(get_session),
):
    """
    Associa uma tag ao ativo
    """
    session.add(AssetTag(asset_id=asset_id, tag_id=tag_id))
    await session.commit()


@router.get(
    "/assets/links/{asset_id}",
    tags=["Asset"],
    response_model=typing.List[AssetLinkItemSchema],
    response_model_exclude_none=False,
)
async def get_links(
    asset_id: UUID = Path(..., description="Identificador"),
    session: AsyncSession = Depends(get_session),
) -> typing.List[AssetLinkItemSchema]:
    """
    Recupera links associados ao ativo
    """
    rows = (
        (
            await session.execute(
                select(AssetLink).filter(AssetLink.asset_id == asset_id)
            )
        )
        .scalars()
        .all()
    )
    return [AssetLinkItemSchema.model_validate(row) for row in list(rows)]


@router.delete("/assets/links/{asset_id}/{link_id}", tags=["Asset"])
async def delete_link(
    asset_id: UUID = Path(..., description="Identificador do ativo"),
    link_id: UUID = Path(..., description="Identificador do link"),
    session: AsyncSession = Depends(get_session),
):
    """
    Exclui uma link associada ao ativo
    """
    await session.execute(
        delete(AssetLink)
        .where(AssetLink.id == link_id)
        .where(AssetLink.asset_id == asset_id)
    )
    await session.commit()


@router.patch("/assets/links/{asset_id}/{link_id}", tags=["Asset"])
async def update_link(
    link_data: AssetLinkCreateSchema,
    asset_id: UUID = Path(..., description="Identificador do ativo"),
    link_id: UUID = Path(..., description="Identificador do link"),
    session: AsyncSession = Depends(get_session),
):
    """
    Atualiza uma link associada ao ativo
    """
    if link_data.url is not None:
        await session.execute(
            update(AssetLink)
            .where(AssetLink.id == link_id)
            .where(AssetLink.asset_id == asset_id)
            .values(
                {
                    AssetLink.url: link_data.url.unicode_string(),
                    AssetLink.type: link_data.type,
                }
            )
        )
    await session.commit()


@router.post("/assets/links/{asset_id}", tags=["Asset"])
async def add_link(
    link_data: AssetLinkCreateSchema,
    asset_id: UUID = Path(..., description="Identificador do ativo"),
    session: AsyncSession = Depends(get_session),
):
    """
    Associa uma link ao ativo
    """
    if link_data.url is not None:
        session.add(
            AssetLink(
                asset_id=asset_id,
                type=link_data.type,
                url=link_data.url.unicode_string(),
            )
        )
    await session.commit()


@router.get(
    "/assets/responsibilities/{asset_id}",
    tags=["Asset"],
    response_model=typing.List[ResponsibilityItemSchema],
    response_model_exclude_none=False,
)
async def get_responsibility(
    asset_id: UUID = Path(..., description="Identificador"),
    session: AsyncSession = Depends(get_session),
) -> typing.List[ResponsibilityItemSchema]:
    """
    Recupera responsáveis associados ao ativo
    """
    rows = (
        (
            await session.execute(
                select(Responsibility)
                .filter(Responsibility.asset_id == asset_id)
                .options(
                    joinedload(Responsibility.type)
                )  # Eagerly loads Responsibility.type
                .options(
                    joinedload(Responsibility.contact)
                )  # Eagerly loads Responsibility.contact
            )
        )
        .scalars()
        .all()
    )
    # breakpoint()
    return [
        ResponsibilityItemSchema.model_validate(
            {"type": row.type, "contact": row.contact}
        )
        for row in list(rows)
    ]


@router.post("/assets/responsibilities/{asset_id}", tags=["Asset"])
async def add_responsibility(
    responsibility_data: ResponsibilityCreateSchema,
    asset_id: UUID = Path(..., description="Identificador do ativo"),
    session: AsyncSession = Depends(get_session),
):
    """
    Associa uma responsabilidade ao ativo
    """
    if (
        responsibility_data.contact_id is not None
        and responsibility_data.type_id is not None
    ):
        session.add(
            Responsibility(
                asset_id=asset_id,
                type_id=responsibility_data.type_id,
                contact_id=responsibility_data.contact_id,
            )
        )
    await session.commit()


@router.delete("/assets/responsibilities/{asset_id}/{contact_id}/{type_id}", tags=["Asset"])
async def delete_responsibility(
    asset_id: UUID = Path(..., description="Identificador do ativo"),
    contact_id: UUID = Path(..., description="Identificador do contato responsável"),
    type_id: UUID = Path(..., description="Identificador do tipo de responsabilidade"),
    session: AsyncSession = Depends(get_session),
):
    """
    Exclui uma responsabilidade associada ao ativo
    """
    await session.execute(
        delete(Responsibility)
        .where(Responsibility.contact_id == contact_id)
        .where(Responsibility.type_id == type_id)
        .where(Responsibility.asset_id == asset_id)
    )
    await session.commit()
