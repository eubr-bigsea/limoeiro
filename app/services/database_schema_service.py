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
    DatabaseSchemaCreateSchema,
    DatabaseSchemaUpdateSchema,
    DatabaseSchemaItemSchema,
    DatabaseSchemaListSchema,
    DatabaseSchemaQuerySchema,
)
from ..models import DatabaseSchema
from . import BaseService

log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


class DatabaseSchemaService(BaseService):
    """Service class implementing business logic for
    DatabaseSchema entities"""

    def __init__(self, session: AsyncSession):
        super().__init__(DatabaseSchema)
        self.session = session

    async def _get(
        self, database_schema_id: UUID
    ) -> typing.Optional[DatabaseSchema]:
        result = await self.session.execute(
            select(DatabaseSchema)
            .options(selectinload(DatabaseSchema.database))
            .filter(DatabaseSchema.id == database_schema_id)
        )
        return result.scalars().first()

    async def _get_by_fqn(self, fully_qualified_name: str) -> typing.Optional[DatabaseSchema]:
        result = await self.session.execute(
            select(DatabaseSchema)
            .options(selectinload(DatabaseSchema.database))
            .filter(DatabaseSchema.fully_qualified_name == fully_qualified_name)
        )
        return result.scalars().first()


    @handle_db_exceptions("Failed to create {}")
    async def add(
        self, database_schema_data: DatabaseSchemaCreateSchema
    ) -> DatabaseSchemaItemSchema:
        """
        Create a new DatabaseSchema instance.

        Args:
            database_schema: The new instance.
        Returns:
            DatabaseSchema: Created instance
        """
        database_schema = DatabaseSchema(
            **database_schema_data.model_dump(exclude_unset=True)
        )
        self.session.add(database_schema)
        await self.session.commit()
        await self.session.refresh(database_schema)
        return DatabaseSchemaItemSchema.model_validate(database_schema)

    @handle_db_exceptions("Failed to delete {}")
    async def delete(
        self, database_schema_id: UUID
    ) -> typing.Optional[DatabaseSchemaItemSchema]:
        """
        Delete DatabaseSchema instance.
        Args:
            database_schema_id: The ID of the DatabaseSchema instance to delete.
        Returns:
            DatabaseSchema: Deleted instance if found or None
        """
        database_schema = await self._get(database_schema_id)
        if database_schema:
            await self.session.delete(database_schema)
            await self.session.commit()
            return DatabaseSchemaItemSchema.model_validate(database_schema)
        return None

    @handle_db_exceptions("Failed to update {}.")
    async def update(
        self,
        database_schema_id: UUID,
        database_schema_data: typing.Optional[DatabaseSchemaUpdateSchema],
    ) -> DatabaseSchemaItemSchema:
        """
        Update a single instance of class DatabaseSchema.
        Args:
            database_schema_id: The ID of the DatabaseSchema instance to update.
            database_schema_data: An object containing the updated fields for the instance.
        Returns:
            DatabaseSchema: The updated instance if found, None otheriwse

        """
        database_schema = await self._get(database_schema_id)
        if not database_schema:
            raise ex.EntityNotFoundException("{cls_name}", database_schema_id)
        if database_schema_data is not None:
            for key, value in database_schema_data.model_dump(
                exclude_unset=True, exclude={}
            ).items():
                setattr(database_schema, key, value)

        await self.session.commit()
        await self.session.refresh(database_schema)
        return DatabaseSchemaItemSchema.model_validate(database_schema)

    @handle_db_exceptions("Failed to retrieve {}")
    async def find(
        self, query_options: DatabaseSchemaQuerySchema
    ) -> PaginatedSchema[DatabaseSchemaListSchema]:
        """
        Retrieve a paginated, sorted list of DatabaseSchema instances.

        Args:

        Returns:
            List[DatabaseSchema]: List of DatabaseSchema instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(DatabaseSchema)
        filter_opts = {
            "database_id": (DatabaseSchema.database_id, "__eq__"),
            "layer_id": (DatabaseSchema.layer_id, "__eq__"),
            "query": (
                (
                    DatabaseSchema.name,
                    DatabaseSchema.display_name,
                    DatabaseSchema.description,
                ),
                "ilike",
            ),
        }
        filters = self.get_filters(DatabaseSchema, filter_opts, query_options)

        if filters:
            query = query.where(and_(*filters))

        if query_options.sort_by and hasattr(
            DatabaseSchema, query_options.sort_by
        ):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(DatabaseSchema, query_options.sort_by))
            )
        # ???
        rows = list(
            (await self.session.execute(query.offset(offset).limit(limit)))
            .scalars()
            .unique()
            .all()
        )

        count_query = select(func.count()).select_from(DatabaseSchema)

        where_clause = query.whereclause
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[DatabaseSchemaListSchema](
            page_size=limit,
            page_count=math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=[DatabaseSchemaListSchema.model_validate(row) for row in rows],
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(self, database_schema_id: UUID) -> DatabaseSchemaItemSchema:
        """
        Retrieve a DatabaseSchema instance by id.
        Args:
            database_schema_id: The ID of the DatabaseSchema instance to retrieve.
        Returns:
            DatabaseSchema: Found instance or None
        """
        return DatabaseSchemaItemSchema.model_validate(
            await self._get(database_schema_id)
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get_by_fqn(self, fully_qualified_name: str) -> DatabaseSchemaItemSchema:
        """
        Retrieve a DatabaseSchema instance by id.
        Args:
            database_schema_id: The ID of the DatabaseSchema instance to retrieve.
        Returns:
            DatabaseSchema: Found instance or None
        """
        result = await self._get_by_fqn(fully_qualified_name)
        if result is not None:
            result = DatabaseSchemaItemSchema.model_validate(result)
        return result
