import logging
import math
import typing
from uuid import UUID
from sqlalchemy import asc, desc, func

import app.exceptions as ex
from ..utils.decorators import handle_db_exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..schemas import (
    BaseQuerySchema,
    PaginatedSchema,
    ResponsibilityTypeItemSchema,
    ResponsibilityTypeListSchema,
)
from ..models import ResponsibilityType
from . import BaseService

log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


class ResponsibilityTypeService(BaseService):
    """Service class implementing business logic for
    ResponsibilityType entities"""

    def __init__(self, session: AsyncSession):
        super().__init__(ResponsibilityType, session)
        self.session = session

    async def _get(
        self, responsibility_type_id: UUID
    ) -> typing.Optional[ResponsibilityType]:
        result = await self.session.execute(
            select(ResponsibilityType).filter(
                ResponsibilityType.id == responsibility_type_id
            )
        )
        return result.scalars().first()

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(
        self, responsibility_type_id: UUID
    ) -> typing.Optional[ResponsibilityTypeItemSchema]:
        """
        Retrieve a ResponsibilityType instance by id.
        Args:
            responsibility_type_id: The ID of the ResponsibilityType instance to retrieve.
        Returns:
            ResponsibilityType: Found instance or None
        """
        responsibility_type = await self._get(responsibility_type_id)
        if responsibility_type:
            return ResponsibilityTypeItemSchema.model_validate(
                responsibility_type
            )
        else:
            raise ex.EntityNotFoundException(
                "ResponsibilityType", responsibility_type_id
            )

    @handle_db_exceptions("Failed to retrieve {}")
    async def find(
        self, query_options: BaseQuerySchema
    ) -> PaginatedSchema[ResponsibilityTypeListSchema]:
        """
        Retrieve a paginated, sorted list of ResponsibilityType instances.

        Args:

        Returns:
            List[ResponsibilityType]: List of ResponsibilityType instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(ResponsibilityType)

        if query_options.sort_by and hasattr(
            ResponsibilityType, query_options.sort_by
        ):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(ResponsibilityType, query_options.sort_by))
            )
        # ???
        rows = list(
            (await self.session.execute(query.offset(offset).limit(limit)))
            .scalars()
            .unique()
            .all()
        )

        count_query = select(func.count()).select_from(ResponsibilityType)

        where_clause = query.whereclause
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[ResponsibilityTypeListSchema](
            page_size=limit,
            page_count=math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=[
                ResponsibilityTypeListSchema.model_validate(row) for row in rows
            ],
        )
