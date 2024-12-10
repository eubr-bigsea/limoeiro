import logging
import math
from uuid import UUID
from sqlalchemy import asc, desc, func
from ..utils.decorators import handle_db_exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..schemas import (
    BaseQuerySchema,
    PaginatedSchema,
)
from ..models import Tag
from . import BaseService
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*

class TagService(BaseService):
    """ Service class implementing business logic for
    Tag entities"""
    def __init__(self, session: AsyncSession ):
        super().__init__(Tag)
        self.session = session

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(self, tag_id: UUID) -> Tag:
        """
        Retrieve a Tag instance by id.
        Args:
            tag_id: The ID of the Tag instance to retrieve.
        Returns:
            Tag: Found instance or None
        """
        result = await self.session.execute(
            select(Tag)
            .filter(Tag.id == tag_id))
        return result.scalars().first()
    @handle_db_exceptions("Failed to retrieve {}")
    async def find(self,
        query_options: BaseQuerySchema
    ) -> PaginatedSchema[Tag]:
        """
        Retrieve a paginated, sorted list of Tag instances.

        Args:

        Returns:
            List[Tag]: List of Tag instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(Tag)

        if (
            query_options.sort_by and
                hasattr(Tag, query_options.sort_by)
        ):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(Tag, query_options.sort_by)))
        rows = (
            await self.session.execute(query.offset(offset).limit(limit))
        ).scalars().unique().all()

        count_query = select(func.count()).select_from(
            query.selectable.with_only_columns(Tag.id)
        )
        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[Tag](
            page_size=limit,
            page_count = math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=rows,
        )
