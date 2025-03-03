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
    DatabaseCreateSchema,
    DatabaseUpdateSchema,
    DatabaseItemSchema,
    DatabaseListSchema,
    DatabaseQuerySchema,
)
from ..models import Database
from . import BaseService

log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


class DatabaseService(BaseService):
    """Service class implementing business logic for
    Database entities"""

    def __init__(self, session: AsyncSession):
        super().__init__(Database, session)
        self.session = session

    async def _get(self, database_id: UUID) -> typing.Optional[Database]:
        result = await self.session.execute(
            select(Database)
            .options(selectinload(Database.provider))
            .filter(Database.id == database_id)
        )
        return result.scalars().first()

    @handle_db_exceptions("Failed to create {}")
    async def add(
        self, database_data: DatabaseCreateSchema
    ) -> DatabaseItemSchema:
        """
        Create a new Database instance.

        Args:
            database: The new instance.
        Returns:
            Database: Created instance
        """
        database = Database(**database_data.model_dump(exclude_unset=True))
        self.session.add(database)
        await self.session.commit()
        await self.session.refresh(database)
        return DatabaseItemSchema.model_validate(database)

    @handle_db_exceptions("Failed to delete {}")
    async def delete(
        self, database_id: UUID
    ) -> typing.Optional[DatabaseItemSchema]:
        """
        Delete Database instance.
        Args:
            database_id: The ID of the Database instance to delete.
        Returns:
            Database: Deleted instance if found or None
        """
        database = await self._get(database_id)
        if database:
            await self.session.delete(database)
            await self.session.commit()
            return DatabaseItemSchema.model_validate(database)
        return None

    @handle_db_exceptions("Failed to update {}.")
    async def update(
        self,
        database_id: UUID,
        database_data: typing.Optional[DatabaseUpdateSchema],
    ) -> DatabaseItemSchema:
        """
        Update a single instance of class Database.
        Args:
            database_id: The ID of the Database instance to update.
            database_data: An object containing the updated fields for the instance.
        Returns:
            Database: The updated instance if found, None otheriwse

        """
        database = await self._get(database_id)
        if not database:
            raise ex.EntityNotFoundException("Database", database_id)
        if database_data is not None:
            for key, value in database_data.model_dump(
                exclude_unset=True, exclude={}
            ).items():
                setattr(database, key, value)

        await self.session.commit()
        await self.session.refresh(database)
        return DatabaseItemSchema.model_validate(database)

    @handle_db_exceptions("Failed to retrieve {}")
    async def find(
        self, query_options: DatabaseQuerySchema
    ) -> PaginatedSchema[DatabaseListSchema]:
        """
        Retrieve a paginated, sorted list of Database instances.

        Args:

        Returns:
            List[Database]: List of Database instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(Database)
        filter_opts = {
            "provider_id": (Database.provider_id, "__eq__"),
            "domain_id": (Database.domain_id, "__eq__"),
            "layer_id": (Database.layer_id, "__eq__"),
            "query": (
                (
                    Database.name,
                    Database.display_name,
                    Database.description,
                ),
                "ilike",
            ),
            "tags": (None, "tag"),
        }
        filters = self.get_filters(Database, filter_opts, query_options)

        if filters:
            query = query.where(and_(*filters))

        if query_options.sort_by and hasattr(Database, query_options.sort_by):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(Database, query_options.sort_by))
            )
        # ???
        rows = list(
            (await self.session.execute(query.offset(offset).limit(limit)))
            .scalars()
            .unique()
            .all()
        )

        count_query = select(func.count()).select_from(Database)

        where_clause = query.whereclause
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[DatabaseListSchema](
            page_size=limit,
            page_count=math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=[DatabaseListSchema.model_validate(row) for row in rows],
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(
        self, database_id: UUID
    ) -> typing.Optional[DatabaseItemSchema]:
        """
        Retrieve a Database instance by id.
        Args:
            database_id: The ID of the Database instance to retrieve.
        Returns:
            Database: Found instance or None
        """
        database = await self._get(database_id)
        if database:
            return DatabaseItemSchema.model_validate(database)
        else:
            raise ex.EntityNotFoundException("Database", database_id)
