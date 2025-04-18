import logging
import math
import typing
from uuid import UUID
from sqlalchemy import asc, desc, and_, func

import app.exceptions as ex
from ..utils.decorators import handle_db_exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from ..schemas import (
    PaginatedSchema,
    DatabaseProviderConnectionCreateSchema,
    DatabaseProviderConnectionUpdateSchema,
    DatabaseProviderConnectionItemSchema,
    DatabaseProviderConnectionListSchema,
    DatabaseProviderConnectionQuerySchema,
)
from ..models import DatabaseProviderConnection
from . import BaseService

log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


class DatabaseProviderConnectionService(BaseService):
    """Service class implementing business logic for
    DatabaseProviderConnection entities"""

    def __init__(self, session: AsyncSession):
        super().__init__(DatabaseProviderConnection, session)
        self.session = session

    @handle_db_exceptions("Failed to create {}")
    async def add(
        self,
        database_provider_connection_data: DatabaseProviderConnectionCreateSchema,
    ) -> DatabaseProviderConnectionItemSchema:
        """
        Create a new DatabaseProviderConnection instance.

        Args:
            database_provider_connection: The new instance.
        Returns:
            DatabaseProviderConnection: Created instance
        """
        database_provider_connection = DatabaseProviderConnection(
            **database_provider_connection_data.model_dump(exclude_unset=True)
        )
        self.session.add(database_provider_connection)
        await self.session.flush()
        await self.session.refresh(database_provider_connection)
        return DatabaseProviderConnectionItemSchema.model_validate(
            database_provider_connection
        )

    @handle_db_exceptions("Failed to delete {}")
    async def delete(
        self, database_provider_connection_id: UUID
    ) -> typing.Optional[DatabaseProviderConnectionItemSchema]:
        """
        Delete DatabaseProviderConnection instance.
        Args:
            database_provider_connection_id: The ID of the DatabaseProviderConnection instance to delete.
        Returns:
            DatabaseProviderConnection: Deleted instance if found or None
        """
        database_provider_connection = await self._get(
            database_provider_connection_id
        )
        if database_provider_connection:
            await self.session.delete(database_provider_connection)
            await self.session.flush()
            return DatabaseProviderConnectionItemSchema.model_validate(
                database_provider_connection
            )
        return None

    @handle_db_exceptions("Failed to update {}.")
    async def update(
        self,
        database_provider_connection_id: UUID,
        database_provider_connection_data: typing.Optional[
            DatabaseProviderConnectionUpdateSchema
        ],
    ) -> DatabaseProviderConnectionItemSchema:
        """
        Update a single instance of class DatabaseProviderConnection.
        Args:
            database_provider_connection_id: The ID of the DatabaseProviderConnection instance to update.
            database_provider_connection_data: An object containing the updated fields for the instance.
        Returns:
            DatabaseProviderConnection: The updated instance if found, None otheriwse

        """
        database_provider_connection = await self._get(
            database_provider_connection_id
        )
        if not database_provider_connection:
            raise ex.EntityNotFoundException(
                "DatabaseProviderConnection", database_provider_connection_id
            )
        if database_provider_connection_data is not None:
            for key, value in database_provider_connection_data.model_dump(
                exclude_unset=True, exclude={}
            ).items():
                setattr(database_provider_connection, key, value)

        await self.session.flush()
        await self.session.refresh(database_provider_connection)
        return DatabaseProviderConnectionItemSchema.model_validate(
            database_provider_connection
        )

    @handle_db_exceptions("Failed to retrieve {}")
    async def find(
        self, query_options: DatabaseProviderConnectionQuerySchema
    ) -> PaginatedSchema[DatabaseProviderConnectionListSchema]:
        """
        Retrieve a paginated, sorted list of DatabaseProviderConnection instances.

        Args:

        Returns:
            List[DatabaseProviderConnection]: List of DatabaseProviderConnection instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(DatabaseProviderConnection)
        filter_opts = {
            "provider_id": (DatabaseProviderConnection.provider_id, "__eq__"),
        }
        filters = self.get_filters(
            DatabaseProviderConnection, filter_opts, query_options
        )

        if filters:
            query = query.where(and_(*filters))

        if query_options.sort_by and hasattr(
            DatabaseProviderConnection, query_options.sort_by
        ):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(
                    getattr(DatabaseProviderConnection, query_options.sort_by)
                )
            )
        rows = (
            (await self.session.execute(query.offset(offset).limit(limit)))
            .scalars()
            .unique()
            .all()
        )

        count_query = select(func.count()).select_from(
            DatabaseProviderConnection
        )

        where_clause = query.whereclause
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[DatabaseProviderConnectionListSchema](
            page_size=limit,
            page_count=math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=[
                DatabaseProviderConnectionListSchema.model_validate(row)
                for row in rows
            ],
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(
        self, database_provider_connection_id: UUID, silent=False
    ) -> typing.Optional[DatabaseProviderConnectionItemSchema]:
        """
        Retrieve a DatabaseProviderConnection instance by id.
        Args:
            database_provider_connection_id: The ID of the DatabaseProviderConnection instance to retrieve.
        Returns:
            DatabaseProviderConnection: Found instance or None
        """
        database_provider_connection = await self._get(
            database_provider_connection_id
        )
        if database_provider_connection:
            return DatabaseProviderConnectionItemSchema.model_validate(
                database_provider_connection
            )
        elif not silent:
            raise ex.EntityNotFoundException(
                "DatabaseProviderConnection", database_provider_connection_id
            )
        else:
            return None

    async def _get(
        self, database_provider_connection_id: UUID
    ) -> typing.Optional[DatabaseProviderConnection]:
        filter_condition = (
            DatabaseProviderConnection.id == database_provider_connection_id
        )
        result = await self.session.execute(
            select(DatabaseProviderConnection)
            .options(selectinload(DatabaseProviderConnection.provider))
            .filter(filter_condition)
        )
        return result.scalars().first()
