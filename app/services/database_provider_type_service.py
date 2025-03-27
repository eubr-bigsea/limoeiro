import logging
import math
import typing
from sqlalchemy import asc, desc, func

import app.exceptions as ex
from ..utils.decorators import handle_db_exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..schemas import (
    BaseQuerySchema,
    PaginatedSchema,
    DatabaseProviderTypeItemSchema,
    DatabaseProviderTypeListSchema,
)
from ..models import DatabaseProviderType
from . import BaseService

log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


class DatabaseProviderTypeService(BaseService):
    """Service class implementing business logic for
    DatabaseProviderType entities"""

    def __init__(self, session: AsyncSession):
        super().__init__(DatabaseProviderType, session)
        self.session = session

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(
        self, database_provider_type_id: int, silent=False
    ) -> typing.Optional[DatabaseProviderTypeItemSchema]:
        """
        Retrieve a DatabaseProviderType instance by id.
        Args:
            database_provider_type_id: The ID of the DatabaseProviderType instance to retrieve.
        Returns:
            DatabaseProviderType: Found instance or None
        """
        database_provider_type = await self._get(database_provider_type_id)
        if database_provider_type:
            return DatabaseProviderTypeItemSchema.model_validate(
                database_provider_type
            )
        elif not silent:
            raise ex.EntityNotFoundException(
                "DatabaseProviderType", database_provider_type_id
            )
        else:
            return None

    @handle_db_exceptions("Failed to retrieve {}")
    async def find(
        self, query_options: BaseQuerySchema
    ) -> PaginatedSchema[DatabaseProviderTypeListSchema]:
        """
        Retrieve a paginated, sorted list of DatabaseProviderType instances.

        Args:

        Returns:
            List[DatabaseProviderType]: List of DatabaseProviderType instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(DatabaseProviderType)

        if query_options.sort_by and hasattr(
            DatabaseProviderType, query_options.sort_by
        ):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(DatabaseProviderType, query_options.sort_by))
            )
        rows = (
            (await self.session.execute(query.offset(offset).limit(limit)))
            .scalars()
            .unique()
            .all()
        )

        count_query = select(func.count()).select_from(DatabaseProviderType)

        where_clause = query.whereclause
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[DatabaseProviderTypeListSchema](
            page_size=limit,
            page_count=math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=[
                DatabaseProviderTypeListSchema.model_validate(row)
                for row in rows
            ],
        )

    async def _get(
        self, database_provider_type_id: int
    ) -> typing.Optional[DatabaseProviderType]:
        filter_condition = DatabaseProviderType.id == database_provider_type_id
        result = await self.session.execute(
            select(DatabaseProviderType).filter(filter_condition)
        )
        return result.scalars().first()
