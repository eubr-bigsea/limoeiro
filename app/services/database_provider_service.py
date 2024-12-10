import logging
import math
from uuid import UUID
from sqlalchemy import asc, desc, and_, func
from ..utils.decorators import handle_db_exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from ..schemas import (
    PaginatedSchema,
    DatabaseProviderCreateSchema,
    DatabaseProviderQuerySchema,
)
from ..models import DatabaseProvider
from . import BaseService
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*

class DatabaseProviderService(BaseService):
    """ Service class implementing business logic for
    DatabaseProvider entities"""
    def __init__(self, session: AsyncSession ):
        super().__init__(DatabaseProvider)
        self.session = session

    @handle_db_exceptions("Failed to create {}")
    async def add(
        self, database_provider_data: DatabaseProviderCreateSchema
    ) -> DatabaseProvider:
        """
        Create a new DatabaseProvider instance.

        Args:
            database_provider: The new instance.
        Returns:
            DatabaseProvider: Created instance
        """
        database_provider = DatabaseProvider(**database_provider_data.model_dump(
            exclude_unset=True))
        self.session.add(database_provider)
        await self.session.commit()
        await self.session.refresh(database_provider)
        return database_provider

    @handle_db_exceptions("Failed to delete {}")
    async def delete(self, database_provider_id: UUID) -> DatabaseProvider:
        """
        Delete DatabaseProvider instance.
        Args:
            database_provider_id: The ID of the DatabaseProvider instance to delete.
        Returns:
            DatabaseProvider: Deleted instance if found or None
        """
        database_provider = await self.get(database_provider_id)
        if database_provider:
            await self.session.delete(database_provider)
            await self.session.commit()
        return database_provider

    @handle_db_exceptions("Failed to update {}")
    async def update(self,
        database_provider_id: UUID,
        database_provider_data: DatabaseProvider) -> DatabaseProvider:
        """
        Update a single instance of class DatabaseProvider.
        Args:
            database_provider_id: The ID of the DatabaseProvider instance to update.
            database_provider_data: An object containing the updated fields for the instance.
        Returns:
            DatabaseProvider: The updated instance if found, None otheriwse

        """
        database_provider = await self.get(database_provider_id)
        if not database_provider:
            return None
        for key, value in database_provider_data.model_dump(
            exclude_unset=True).items():
            setattr(database_provider, key, value)
        await self.session.commit()
        await self.session.refresh(database_provider)

        return database_provider
    @handle_db_exceptions("Failed to retrieve {}")
    async def find(self,
        query_options: DatabaseProviderQuerySchema
    ) -> PaginatedSchema[DatabaseProvider]:
        """
        Retrieve a paginated, sorted list of DatabaseProvider instances.

        Args:

        Returns:
            List[DatabaseProvider]: List of DatabaseProvider instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(DatabaseProvider)
        filter_opts = {
            "provider_type_id": (DatabaseProvider.provider_type_id, "__eq__"),
            "domain_id": (DatabaseProvider.domain_id, "__eq__"),
            "layer_id": (DatabaseProvider.layer_id, "__eq__"),
            "query": ((
               DatabaseProvider.name,
               DatabaseProvider.display_name,
               DatabaseProvider.description,
            ), "ilike"),
        }
        filters = self.get_filters(DatabaseProvider, filter_opts, query_options)

        if filters:
            query = query.where(and_(*filters))

        if (
            query_options.sort_by and
                hasattr(DatabaseProvider, query_options.sort_by)
        ):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(DatabaseProvider, query_options.sort_by)))
        rows = (
            await self.session.execute(query.offset(offset).limit(limit))
        ).scalars().unique().all()

        count_query = select(func.count()).select_from(
            query.selectable.with_only_columns(DatabaseProvider.id)
        )
        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[DatabaseProvider](
            page_size=limit,
            page_count = math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=rows,
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(self, database_provider_id: UUID) -> DatabaseProvider:
        """
        Retrieve a DatabaseProvider instance by id.
        Args:
            database_provider_id: The ID of the DatabaseProvider instance to retrieve.
        Returns:
            DatabaseProvider: Found instance or None
        """
        result = await self.session.execute(
            select(DatabaseProvider)
            .options(selectinload(DatabaseProvider.provider_type))
            .options(selectinload(DatabaseProvider.domain))
            .options(selectinload(DatabaseProvider.layer))
            .options(selectinload(DatabaseProvider.connection))
            .options(selectinload(DatabaseProvider.ingestions))
            .filter(DatabaseProvider.id == database_provider_id))
        return result.scalars().first()
