import logging
import math
import typing
from sqlalchemy import asc, desc, func

from ..utils.decorators import handle_db_exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..schemas import (
    BaseQuerySchema,
    PaginatedSchema,
    PermissionListSchema,
)
from ..models import Permission
from . import BaseService

log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


class PermissionService(BaseService):
    """Service class implementing business logic for
    Permission entities"""

    def __init__(self, session: AsyncSession):
        super().__init__(Permission, session)
        self.session = session

    @handle_db_exceptions("Failed to retrieve {}")
    async def find(
        self, query_options: BaseQuerySchema
    ) -> PaginatedSchema[PermissionListSchema]:
        """
        Retrieve a paginated, sorted list of Permission instances.

        Args:

        Returns:
            List[Permission]: List of Permission instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(Permission)

        if query_options.sort_by and hasattr(Permission, query_options.sort_by):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(Permission, query_options.sort_by))
            )
        else:
            query = query.order_by(Permission.id)
        rows = (
            (await self.session.execute(query.offset(offset).limit(limit)))
            .scalars()
            .unique()
            .all()
        )

        count_query = select(func.count()).select_from(Permission)

        where_clause = query.whereclause
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[PermissionListSchema](
            page_size=limit,
            page_count=math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=[PermissionListSchema.model_validate(row) for row in rows],
        )

    async def _get(self, permission_id: int) -> typing.Optional[Permission]:
        filter_condition = ()
        result = await self.session.execute(
            select(Permission).filter(filter_condition)
        )
        return result.scalars().first()
