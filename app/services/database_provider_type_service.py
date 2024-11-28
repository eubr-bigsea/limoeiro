import logging
import typing
from sqlalchemy import asc, desc
from ..utils.decorators import handle_db_exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..schemas import (
    BaseQuerySchema,
)
from ..models import DatabaseProviderType
from . import BaseService
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*

class DatabaseProviderTypeService(BaseService):
    """ Service class implementing business logic for
    DatabaseProviderType entities"""
    def __init__(self, session: AsyncSession ):
        super().__init__(DatabaseProviderType)
        self.session = session

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(self, database_provider_type_id: int) -> DatabaseProviderType:
        """
        Retrieve a DatabaseProviderType instance by id.
        Args:
            database_provider_type_id: The ID of the DatabaseProviderType instance to retrieve.
        Returns:
            DatabaseProviderType: Found instance or None
        """
        result = await self.session.execute(
            select(DatabaseProviderType)
            .filter(DatabaseProviderType.id == database_provider_type_id))
        return result.scalars().first()
    @handle_db_exceptions("Failed to retrieve {}")
    async def find(self,
        query_options: BaseQuerySchema
    ) -> typing.List[DatabaseProviderType]:
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

        if (
            query_options.sort_by and
                hasattr(DatabaseProviderType, query_options.sort_by)
        ):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(DatabaseProviderType, query_options.sort_by)))

        result = await self.session.execute(
            query.offset(offset).limit(limit))
        return result.scalars().unique().all()
