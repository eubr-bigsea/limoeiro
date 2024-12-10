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
    DatabaseTableCreateSchema,
    DatabaseTableQuerySchema,
)
from ..models import DatabaseTable, TableColumn
from . import BaseService
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*

class DatabaseTableService(BaseService):
    """ Service class implementing business logic for
    DatabaseTable entities"""
    def __init__(self, session: AsyncSession ):
        super().__init__(DatabaseTable)
        self.session = session

    @handle_db_exceptions("Failed to create {}")
    async def add(
        self, database_table_data: DatabaseTableCreateSchema
    ) -> DatabaseTable:
        """
        Create a new DatabaseTable instance.

        Args:
            database_table: The new instance.
        Returns:
            DatabaseTable: Created instance
        """
        exclude = { "columns", }
        database_table = DatabaseTable(**database_table_data.model_dump(
            exclude_unset=True, exclude=exclude))

        # Update "many" side from one to many when association is a composition
        # Add TableColumn to the DatabaseTable
        for columns_data in database_table_data.columns:
            new_columns = TableColumn(**columns_data.model_dump(
                exclude_unset=True))
            database_table.columns.append(new_columns)
        
        self.session.add(database_table)
        await self.session.commit()
        await self.session.refresh(database_table)
        return database_table

    @handle_db_exceptions("Failed to delete {}")
    async def delete(self, database_table_id: UUID) -> DatabaseTable:
        """
        Delete DatabaseTable instance.
        Args:
            database_table_id: The ID of the DatabaseTable instance to delete.
        Returns:
            DatabaseTable: Deleted instance if found or None
        """
        database_table = await self.get(database_table_id)
        if database_table:
            await self.session.delete(database_table)
            await self.session.commit()
        return database_table

    @handle_db_exceptions("Failed to update {}")
    async def update(self,
        database_table_id: UUID,
        database_table_data: DatabaseTable) -> DatabaseTable:
        """
        Update a single instance of class DatabaseTable.
        Args:
            database_table_id: The ID of the DatabaseTable instance to update.
            database_table_data: An object containing the updated fields for the instance.
        Returns:
            DatabaseTable: The updated instance if found, None otheriwse

        """
        database_table = await self.get(database_table_id)
        if not database_table:
            return None
        for key, value in database_table_data.model_dump(
            exclude_unset=True).items():
            setattr(database_table, key, value)
        await self.session.commit()
        await self.session.refresh(database_table)

        return database_table
    @handle_db_exceptions("Failed to retrieve {}")
    async def find(self,
        query_options: DatabaseTableQuerySchema
    ) -> PaginatedSchema[DatabaseTable]:
        """
        Retrieve a paginated, sorted list of DatabaseTable instances.

        Args:

        Returns:
            List[DatabaseTable]: List of DatabaseTable instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(DatabaseTable)
        filter_opts = {
            "database_id": (DatabaseTable.database_id, "__eq__"),
            "database_schema_id": (DatabaseTable.database_schema_id, "__eq__"),
            "layer_id": (DatabaseTable.layer_id, "__eq__"),
            "query": ((
               DatabaseTable.name,
               DatabaseTable.display_name,
               DatabaseTable.description,
            ), "ilike"),
        }
        filters = self.get_filters(DatabaseTable, filter_opts, query_options)

        if filters:
            query = query.where(and_(*filters))

        if (
            query_options.sort_by and
                hasattr(DatabaseTable, query_options.sort_by)
        ):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(DatabaseTable, query_options.sort_by)))
        rows = (
            await self.session.execute(query.offset(offset).limit(limit))
        ).scalars().unique().all()

        count_query = select(func.count()).select_from(
            query.selectable.with_only_columns(DatabaseTable.id)
        )
        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[DatabaseTable](
            page_size=limit,
            page_count = math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=rows,
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(self, database_table_id: UUID) -> DatabaseTable:
        """
        Retrieve a DatabaseTable instance by id.
        Args:
            database_table_id: The ID of the DatabaseTable instance to retrieve.
        Returns:
            DatabaseTable: Found instance or None
        """
        result = await self.session.execute(
            select(DatabaseTable)
            .options(selectinload(DatabaseTable.database))
            .options(selectinload(DatabaseTable.database_schema))
            .options(selectinload(DatabaseTable.layer))
            .options(selectinload(DatabaseTable.columns))
            .options(selectinload(DatabaseTable.tags))
            .filter(DatabaseTable.id == database_table_id))
        return result.scalars().first()
