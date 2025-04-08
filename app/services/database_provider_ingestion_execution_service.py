import logging
import math
import typing
from sqlalchemy import asc, desc, and_, func

import app.exceptions as ex
from ..utils.decorators import handle_db_exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from ..schemas import (
    PaginatedSchema,
    DatabaseProviderIngestionExecutionCreateSchema,
    DatabaseProviderIngestionExecutionUpdateSchema,
    DatabaseProviderIngestionExecutionItemSchema,
    DatabaseProviderIngestionExecutionListSchema,
    DatabaseProviderIngestionExecutionQuerySchema,
)
from ..models import DatabaseProviderIngestionExecution
from . import BaseService

log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


class DatabaseProviderIngestionExecutionService(BaseService):
    """Service class implementing business logic for
    DatabaseProviderIngestionExecution entities"""

    def __init__(self, session: AsyncSession):
        super().__init__(DatabaseProviderIngestionExecution, session)
        self.session = session

    @handle_db_exceptions("Failed to create {}")
    async def add(
        self,
        database_provider_ingestion_execution_data: DatabaseProviderIngestionExecutionCreateSchema,
    ) -> DatabaseProviderIngestionExecutionItemSchema:
        """
        Create a new DatabaseProviderIngestionExecution instance.

        Args:
            database_provider_ingestion_execution: The new instance.
        Returns:
            DatabaseProviderIngestionExecution: Created instance
        """
        database_provider_ingestion_execution = (
            DatabaseProviderIngestionExecution(
                **database_provider_ingestion_execution_data.model_dump(
                    exclude_unset=True
                )
            )
        )
        self.session.add(database_provider_ingestion_execution)
        await self.session.flush()
        await self.session.refresh(database_provider_ingestion_execution)
        return DatabaseProviderIngestionExecutionItemSchema.model_validate(
            database_provider_ingestion_execution
        )

    @handle_db_exceptions("Failed to delete {}")
    async def delete(
        self, database_provider_ingestion_execution_id: int
    ) -> typing.Optional[DatabaseProviderIngestionExecutionItemSchema]:
        """
        Delete DatabaseProviderIngestionExecution instance.
        Args:
            database_provider_ingestion_execution_id: The ID of the DatabaseProviderIngestionExecution instance to delete.
        Returns:
            DatabaseProviderIngestionExecution: Deleted instance if found or None
        """
        database_provider_ingestion_execution = await self._get(
            database_provider_ingestion_execution_id
        )
        if database_provider_ingestion_execution:
            await self.session.delete(database_provider_ingestion_execution)
            await self.session.flush()
            return DatabaseProviderIngestionExecutionItemSchema.model_validate(
                database_provider_ingestion_execution
            )
        return None

    @handle_db_exceptions("Failed to update {}.")
    async def update(
        self,
        database_provider_ingestion_execution_id: int,
        database_provider_ingestion_execution_data: typing.Optional[
            DatabaseProviderIngestionExecutionUpdateSchema
        ],
    ) -> DatabaseProviderIngestionExecutionItemSchema:
        """
        Update a single instance of class DatabaseProviderIngestionExecution.
        Args:
            database_provider_ingestion_execution_id: The ID of the DatabaseProviderIngestionExecution instance to update.
            database_provider_ingestion_execution_data: An object containing the updated fields for the instance.
        Returns:
            DatabaseProviderIngestionExecution: The updated instance if found, None otheriwse

        """
        database_provider_ingestion_execution = await self._get(
            database_provider_ingestion_execution_id
        )
        if not database_provider_ingestion_execution:
            raise ex.EntityNotFoundException(
                "DatabaseProviderIngestionExecution",
                database_provider_ingestion_execution_id,
            )
        if database_provider_ingestion_execution_data is not None:
            for (
                key,
                value,
            ) in database_provider_ingestion_execution_data.model_dump(
                exclude_unset=True, exclude={}
            ).items():
                setattr(database_provider_ingestion_execution, key, value)

        await self.session.flush()
        await self.session.refresh(database_provider_ingestion_execution)
        return DatabaseProviderIngestionExecutionItemSchema.model_validate(
            database_provider_ingestion_execution
        )

    @handle_db_exceptions("Failed to retrieve {}")
    async def find(
        self, query_options: DatabaseProviderIngestionExecutionQuerySchema
    ) -> PaginatedSchema[DatabaseProviderIngestionExecutionListSchema]:
        """
        Retrieve a paginated, sorted list of DatabaseProviderIngestionExecution instances.

        Args:

        Returns:
            List[DatabaseProviderIngestionExecution]: List of DatabaseProviderIngestionExecution instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(DatabaseProviderIngestionExecution)
        filter_opts = {
            "ingestion_id": (
                DatabaseProviderIngestionExecution.ingestion_id,
                "__eq__",
            ),
            "status": (DatabaseProviderIngestionExecution.status, "__eq__"),
            "trigger_mode": (
                DatabaseProviderIngestionExecution.trigger_mode,
                "__eq__",
            ),
        }
        filters = self.get_filters(
            DatabaseProviderIngestionExecution, filter_opts, query_options
        )

        if filters:
            query = query.where(and_(*filters))

        if query_options.sort_by and hasattr(
            DatabaseProviderIngestionExecution, query_options.sort_by
        ):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(
                    getattr(
                        DatabaseProviderIngestionExecution, query_options.sort_by
                    )
                )
            )
        rows = (
            (await self.session.execute(query.offset(offset).limit(limit)))
            .scalars()
            .unique()
            .all()
        )

        count_query = select(func.count()).select_from(
            DatabaseProviderIngestionExecution
        )

        where_clause = query.whereclause
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[DatabaseProviderIngestionExecutionListSchema](
            page_size=limit,
            page_count=math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=[
                DatabaseProviderIngestionExecutionListSchema.model_validate(row)
                for row in rows
            ],
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(
        self, database_provider_ingestion_execution_id: int, silent=False
    ) -> typing.Optional[DatabaseProviderIngestionExecutionItemSchema]:
        """
        Retrieve a DatabaseProviderIngestionExecution instance by id.
        Args:
            database_provider_ingestion_execution_id: The ID of the DatabaseProviderIngestionExecution instance to retrieve.
        Returns:
            DatabaseProviderIngestionExecution: Found instance or None
        """
        database_provider_ingestion_execution = await self._get(
            database_provider_ingestion_execution_id
        )
        if database_provider_ingestion_execution:
            return DatabaseProviderIngestionExecutionItemSchema.model_validate(
                database_provider_ingestion_execution
            )
        elif not silent:
            raise ex.EntityNotFoundException(
                "DatabaseProviderIngestionExecution",
                database_provider_ingestion_execution_id,
            )
        else:
            return None

    async def _get(
        self, database_provider_ingestion_execution_id: int
    ) -> typing.Optional[DatabaseProviderIngestionExecution]:
        filter_condition = (
            DatabaseProviderIngestionExecution.id
            == database_provider_ingestion_execution_id
        )
        result = await self.session.execute(
            select(DatabaseProviderIngestionExecution)
            .options(
                selectinload(DatabaseProviderIngestionExecution.triggered_by)
            )
            .options(selectinload(DatabaseProviderIngestionExecution.ingestion))
            .options(selectinload(DatabaseProviderIngestionExecution.logs))
            .filter(filter_condition)
        )
        return result.scalars().first()
