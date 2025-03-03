import logging
import math
import typing
from sqlalchemy import asc, desc, and_, func

import app.exceptions as ex
from ..utils.decorators import handle_db_exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from ..schemas import (
    PaginatedSchema,
    ResponsibilityCreateSchema,
    ResponsibilityUpdateSchema,
    ResponsibilityItemSchema,
    ResponsibilityListSchema,
    ResponsibilityQuerySchema,
)
from ..models import Responsibility
from . import BaseService

log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


class ResponsibilityService(BaseService):
    """Service class implementing business logic for
    Responsibility entities"""

    def __init__(self, session: AsyncSession):
        super().__init__(Responsibility, session)
        self.session = session

    async def _get(
        self, responsibility_id: int
    ) -> typing.Optional[Responsibility]:
        result = await self.session.execute(
            select(Responsibility)
            .options(selectinload(Responsibility.contact))
            .options(selectinload(Responsibility.type))
            .options(selectinload(Responsibility.asset))
            .filter(Responsibility.id == responsibility_id)
        )
        return result.scalars().first()

    @handle_db_exceptions("Failed to create {}")
    async def add(
        self, responsibility_data: ResponsibilityCreateSchema
    ) -> ResponsibilityItemSchema:
        """
        Create a new Responsibility instance.

        Args:
            responsibility: The new instance.
        Returns:
            Responsibility: Created instance
        """
        responsibility = Responsibility(
            **responsibility_data.model_dump(exclude_unset=True)
        )
        self.session.add(responsibility)
        await self.session.commit()
        await self.session.refresh(responsibility)
        return ResponsibilityItemSchema.model_validate(responsibility)

    @handle_db_exceptions("Failed to delete {}")
    async def delete(
        self, responsibility_id: int
    ) -> typing.Optional[ResponsibilityItemSchema]:
        """
        Delete Responsibility instance.
        Args:
            responsibility_id: The ID of the Responsibility instance to delete.
        Returns:
            Responsibility: Deleted instance if found or None
        """
        responsibility = await self._get(responsibility_id)
        if responsibility:
            await self.session.delete(responsibility)
            await self.session.commit()
            return ResponsibilityItemSchema.model_validate(responsibility)
        return None

    @handle_db_exceptions("Failed to update {}.")
    async def update(
        self,
        responsibility_id: int,
        responsibility_data: typing.Optional[ResponsibilityUpdateSchema],
    ) -> ResponsibilityItemSchema:
        """
        Update a single instance of class Responsibility.
        Args:
            responsibility_id: The ID of the Responsibility instance to update.
            responsibility_data: An object containing the updated fields for the instance.
        Returns:
            Responsibility: The updated instance if found, None otheriwse

        """
        responsibility = await self._get(responsibility_id)
        if not responsibility:
            raise ex.EntityNotFoundException("Responsibility", responsibility_id)
        if responsibility_data is not None:
            for key, value in responsibility_data.model_dump(
                exclude_unset=True, exclude={}
            ).items():
                setattr(responsibility, key, value)

        await self.session.commit()
        await self.session.refresh(responsibility)
        return ResponsibilityItemSchema.model_validate(responsibility)

    @handle_db_exceptions("Failed to retrieve {}")
    async def find(
        self, query_options: ResponsibilityQuerySchema
    ) -> PaginatedSchema[ResponsibilityListSchema]:
        """
        Retrieve a paginated, sorted list of Responsibility instances.

        Args:

        Returns:
            List[Responsibility]: List of Responsibility instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(Responsibility)
        filter_opts = {
            "query": (
                (
                    Responsibility.name,
                    Responsibility.description,
                ),
                "ilike",
            ),
        }
        filters = self.get_filters(Responsibility, filter_opts, query_options)

        if filters:
            query = query.where(and_(*filters))

        if query_options.sort_by and hasattr(
            Responsibility, query_options.sort_by
        ):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(Responsibility, query_options.sort_by))
            )
        # ???
        rows = list(
            (await self.session.execute(query.offset(offset).limit(limit)))
            .scalars()
            .unique()
            .all()
        )

        count_query = select(func.count()).select_from(Responsibility)

        where_clause = query.whereclause
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[ResponsibilityListSchema](
            page_size=limit,
            page_count=math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=[ResponsibilityListSchema.model_validate(row) for row in rows],
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(
        self, responsibility_id: int
    ) -> typing.Optional[ResponsibilityItemSchema]:
        """
        Retrieve a Responsibility instance by id.
        Args:
            responsibility_id: The ID of the Responsibility instance to retrieve.
        Returns:
            Responsibility: Found instance or None
        """
        responsibility = await self._get(responsibility_id)
        if responsibility:
            return ResponsibilityItemSchema.model_validate(responsibility)
        else:
            raise ex.EntityNotFoundException("Responsibility", responsibility_id)
