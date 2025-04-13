import logging
import math
import typing
from sqlalchemy import asc, desc, and_, func

from ..utils.decorators import handle_db_exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from ..schemas import (
    PaginatedSchema,
    DatabaseProviderIngestionLogListSchema,
    DatabaseProviderIngestionLogQuerySchema,
)
from ..models import DatabaseProviderIngestionLog
from . import BaseService

log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


class DatabaseProviderIngestionLogService(BaseService):
    """Service class implementing business logic for
    DatabaseProviderIngestionLog entities"""

    def __init__(self, session: AsyncSession):
        super().__init__(DatabaseProviderIngestionLog, session)
        self.session = session

    @handle_db_exceptions("Failed to retrieve {}")
    async def find(
        self, query_options: DatabaseProviderIngestionLogQuerySchema
    ) -> PaginatedSchema[DatabaseProviderIngestionLogListSchema]:
        """
        Retrieve a paginated, sorted list of DatabaseProviderIngestionLog instances.

        Args:

        Returns:
            List[DatabaseProviderIngestionLog]: List of DatabaseProviderIngestionLog instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(DatabaseProviderIngestionLog)
        filter_opts = {
            "execution_id": (
                DatabaseProviderIngestionLog.execution_id,
                "__eq__",
            ),
        }
        filters = self.get_filters(
            DatabaseProviderIngestionLog, filter_opts, query_options
        )

        if filters:
            query = query.where(and_(*filters))

        if query_options.sort_by and hasattr(
            DatabaseProviderIngestionLog, query_options.sort_by
        ):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(
                    getattr(DatabaseProviderIngestionLog, query_options.sort_by)
                )
            )
        rows = (
            (await self.session.execute(query.offset(offset).limit(limit)))
            .scalars()
            .unique()
            .all()
        )

        count_query = select(func.count()).select_from(
            DatabaseProviderIngestionLog
        )

        where_clause = query.whereclause
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[DatabaseProviderIngestionLogListSchema](
            page_size=limit,
            page_count=math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=[
                DatabaseProviderIngestionLogListSchema.model_validate(row)
                for row in rows
            ],
        )

    async def _get(
        self, database_provider_ingestion_log_id: int
    ) -> typing.Optional[DatabaseProviderIngestionLog]:
        filter_condition = ()
        result = await self.session.execute(
            select(DatabaseProviderIngestionLog)
            .options(selectinload(DatabaseProviderIngestionLog.ingestion))
            .options(selectinload(DatabaseProviderIngestionLog.execution))
            .filter(filter_condition)
        )
        return result.scalars().first()
