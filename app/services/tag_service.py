import logging
import math
from uuid import UUID
from sqlalchemy import asc, desc, and_, func
from ..utils.decorators import handle_db_exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..schemas import (
    PaginatedSchema,
    TagCreateSchema,
    TagQuerySchema,
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

    @handle_db_exceptions("Failed to create {}")
    async def add(
        self, tag_data: TagCreateSchema
    ) -> Tag:
        """
        Create a new Tag instance.

        Args:
            tag: The new instance.
        Returns:
            Tag: Created instance
        """
        tag = Tag(**tag_data.model_dump(
            exclude_unset=True))
        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag)
        return tag

    @handle_db_exceptions("Failed to delete {}")
    async def delete(self, tag_id: UUID) -> Tag:
        """
        Delete Tag instance.
        Args:
            tag_id: The ID of the Tag instance to delete.
        Returns:
            Tag: Deleted instance if found or None
        """
        tag = await self.get(tag_id)
        if tag:
            await self.session.delete(tag)
            await self.session.commit()
        return tag

    @handle_db_exceptions("Failed to update {}")
    async def update(self,
        tag_id: UUID,
        tag_data: Tag) -> Tag:
        """
        Update a single instance of class Tag.
        Args:
            tag_id: The ID of the Tag instance to update.
            tag_data: An object containing the updated fields for the instance.
        Returns:
            Tag: The updated instance if found, None otheriwse

        """
        tag = await self.get(tag_id)
        if not tag:
            return None
        for key, value in tag_data.model_dump(
            exclude_unset=True).items():
            setattr(tag, key, value)
        await self.session.commit()
        await self.session.refresh(tag)

        return tag
    @handle_db_exceptions("Failed to retrieve {}")
    async def find(self,
        query_options: TagQuerySchema
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
        filter_opts = {
            "query": ((
               Tag.name,
               Tag.description,
            ), "ilike"),
        }
        filters = self.get_filters(Tag, filter_opts, query_options)

        if filters:
            query = query.where(and_(*filters))

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
