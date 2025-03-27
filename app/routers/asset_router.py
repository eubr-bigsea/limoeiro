#
import logging
import math
import typing
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy import and_, asc, delete, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models import Asset, AssetLink, AssetTag, Responsibility, Tag
from app.routers import get_lookup_filter

from ..database import get_session
from fastapi import HTTPException
from ..schemas import (
    AssetLinkCreateSchema,
    AssetLinkItemSchema,
    AssetListSchema,
    AssetQuerySchema,
    DatabaseListSchema,
    DatabaseProviderListSchema,
    DatabaseSchemaListSchema,
    DatabaseTableListSchema,
    PaginatedSchema,
    ResponsibilityCreateSchema,
    ResponsibilityItemSchema,
    TagItemSchema,
)

router = APIRouter()
log = logging.getLogger(__name__)


@router.get(
    "/assets/",
    tags=["Asset"],
    response_model=PaginatedSchema[AssetListSchema],
    response_model_exclude_none=True,
)
async def find_assets(
    query_options: AssetQuerySchema = Query(),
    session: AsyncSession = Depends(get_session),
) -> PaginatedSchema[AssetListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    page = max(query_options.page, 1)
    limit = min(max(1, query_options.page_size), 100)
    offset = (page - 1) * limit

    query = select(Asset).options(
        selectinload(Asset.domain),  # Load domain if it exists
        selectinload(Asset.layer),
    )
    filters = []
    if query_options.query:
        filters.append(
            or_(
                *(
                    getattr(c, "ilike")(f"%{query_options.query}%")
                    for c in (
                        Asset.name,
                        Asset.description,
                    )
                )
            )
        )
    # if query_options.domain_id:
    #     filters.append(Asset.domain_id.in_([]))
    if query_options.asset_type:
        filters.append(Asset.asset_type.in_(query_options.asset_type))
    if filters:
        query = query.where(and_(*filters))

    if query_options.sort_by and hasattr(Asset, query_options.sort_by):
        order_func = asc if query_options.sort_order != "desc" else desc
        query = query.order_by(order_func(getattr(Asset, query_options.sort_by)))

    rows = list(
        (await session.execute(query.offset(offset).limit(limit)))
        .scalars()
        .unique()
        .all()
    )

    count_query = select(func.count()).select_from(Asset)

    where_clause = query.whereclause
    if where_clause is not None:
        count_query = count_query.where(where_clause)

    total_rows = (await session.execute(count_query)).scalar_one()

    asset_type_to_pydantic = {
        "provider": DatabaseProviderListSchema,
        "database": DatabaseListSchema,
        "schema": DatabaseSchemaListSchema,
        "table": DatabaseTableListSchema,
    }
    return PaginatedSchema[AssetListSchema](
        page_size=limit,
        page_count=math.ceil(total_rows / limit),
        page=page,
        count=total_rows,
        items=[
            # asset_type_to_pydantic[row.asset_type].model_validate(row)
            AssetListSchema.model_validate(row)
            for row in rows
        ],
    )
    # sql = select(Asset).order_by(Asset.name)
    # rows = (await session.execute(sql)).scalars().all()
    # limit = 10
    # total_rows = 100
    # page = 1
    # return PaginatedSchema[AssetListSchema](
    #     page_size=limit,
    #     page_count=math.ceil(total_rows / limit),
    #     page=page,
    #     count=total_rows,
    #     items=[AssetListSchema.model_validate(row) for row in rows],
    # )


@router.options(
    "/assets/{entity_id}",
    tags=["Asset"],
)
async def exists(
    asset_id: typing.Union[UUID, str] = Depends(get_lookup_filter),
    session: AsyncSession = Depends(get_session),
):
    filter_condition = (
        Asset.id == asset_id
        if isinstance(asset_id, UUID)
        else Asset.fully_qualified_name == asset_id
    )

    sql = select(func.count()).select_from(Asset).where(filter_condition)
    exists = (await session.execute(sql)).scalar_one() > 0
    if exists:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=404, detail="Asset not found")


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
                    joinedload(Responsibility.type),
                    joinedload(Responsibility.contact),
                )  # Eagerly loads Responsibility.type and Responsibility.contact
            )
        )
        .scalars()
        .all()
    )
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


@router.delete(
    "/assets/responsibilities/{asset_id}/{contact_id}/{type_id}", tags=["Asset"]
)
async def delete_responsibility(
    asset_id: UUID = Path(..., description="Identificador do ativo"),
    contact_id: UUID = Path(
        ..., description="Identificador do contato responsável"
    ),
    type_id: UUID = Path(
        ..., description="Identificador do tipo de responsabilidade"
    ),
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


@router.patch("/assets/disable-many", tags=["Asset"])
async def disable_many(
    ids: typing.List[str],
    session: AsyncSession = Depends(get_session),
):
    """"""
    await session.execute(
        update(Asset).where(Asset.id.in_(ids)).values(deleted=True)
    )
    await session.commit()
    return {"status": "success", "message": "Assets disabled successfully"}
