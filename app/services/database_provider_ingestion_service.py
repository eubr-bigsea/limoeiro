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
    DatabaseProviderIngestionCreateSchema,
    DatabaseProviderIngestionUpdateSchema,
    DatabaseProviderIngestionItemSchema,
    DatabaseProviderIngestionListSchema,
    DatabaseProviderIngestionQuerySchema,
)
from ..models import DatabaseProviderIngestion
from . import BaseService

log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


class DatabaseProviderIngestionService(BaseService):
    """Service class implementing business logic for
    DatabaseProviderIngestion entities"""

    def __init__(self, session: AsyncSession):
        super().__init__(DatabaseProviderIngestion, session)
        self.session = session

    @handle_db_exceptions("Failed to create {}")
    async def add(
        self,
        database_provider_ingestion_data: DatabaseProviderIngestionCreateSchema,
    ) -> DatabaseProviderIngestionItemSchema:
        """
        Create a new DatabaseProviderIngestion instance.

        Args:
            database_provider_ingestion: The new instance.
        Returns:
            DatabaseProviderIngestion: Created instance
        """
        database_provider_ingestion = DatabaseProviderIngestion(
            **database_provider_ingestion_data.model_dump(exclude_unset=True)
        )
        self.session.add(database_provider_ingestion)
        await self.session.flush()
        await self.session.refresh(database_provider_ingestion)
        return DatabaseProviderIngestionItemSchema.model_validate(
            database_provider_ingestion
        )

    @handle_db_exceptions("Failed to delete {}")
    async def delete(
        self, database_provider_ingestion_id: UUID
    ) -> typing.Optional[DatabaseProviderIngestionItemSchema]:
        """
        Delete DatabaseProviderIngestion instance.
        Args:
            database_provider_ingestion_id: The ID of the DatabaseProviderIngestion instance to delete.
        Returns:
            DatabaseProviderIngestion: Deleted instance if found or None
        """
        database_provider_ingestion = await self._get(
            database_provider_ingestion_id
        )
        if database_provider_ingestion:
            await self.session.delete(database_provider_ingestion)
            await self.session.flush()
            return DatabaseProviderIngestionItemSchema.model_validate(
                database_provider_ingestion
            )
        return None

    @handle_db_exceptions("Failed to update {}.")
    async def update(
        self,
        database_provider_ingestion_id: UUID,
        database_provider_ingestion_data: typing.Optional[
            DatabaseProviderIngestionUpdateSchema
        ],
    ) -> DatabaseProviderIngestionItemSchema:
        """
        Update a single instance of class DatabaseProviderIngestion.
        Args:
            database_provider_ingestion_id: The ID of the DatabaseProviderIngestion instance to update.
            database_provider_ingestion_data: An object containing the updated fields for the instance.
        Returns:
            DatabaseProviderIngestion: The updated instance if found, None otheriwse

        """
        database_provider_ingestion = await self._get(
            database_provider_ingestion_id
        )
        if not database_provider_ingestion:
            raise ex.EntityNotFoundException(
                "DatabaseProviderIngestion", database_provider_ingestion_id
            )
        if database_provider_ingestion_data is not None:
            for key, value in database_provider_ingestion_data.model_dump(
                exclude_unset=True, exclude={}
            ).items():
                setattr(database_provider_ingestion, key, value)

        await self.session.flush()
        await self.session.refresh(database_provider_ingestion)
        return DatabaseProviderIngestionItemSchema.model_validate(
            database_provider_ingestion
        )

    @handle_db_exceptions("Failed to retrieve {}")
    async def find(
        self, query_options: DatabaseProviderIngestionQuerySchema
    ) -> PaginatedSchema[DatabaseProviderIngestionListSchema]:
        """
        Retrieve a paginated, sorted list of DatabaseProviderIngestion instances.

        Args:

        Returns:
            List[DatabaseProviderIngestion]: List of DatabaseProviderIngestion instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(DatabaseProviderIngestion)
        filter_opts = {
            "provider_id": (DatabaseProviderIngestion.provider_id, "__eq__"),
        }
        filters = self.get_filters(
            DatabaseProviderIngestion, filter_opts, query_options
        )

        if filters:
            query = query.where(and_(*filters))

        if query_options.sort_by and hasattr(
            DatabaseProviderIngestion, query_options.sort_by
        ):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(
                    getattr(DatabaseProviderIngestion, query_options.sort_by)
                )
            )
        rows = (
            (await self.session.execute(query.offset(offset).limit(limit)))
            .scalars()
            .unique()
            .all()
        )

        count_query = select(func.count()).select_from(DatabaseProviderIngestion)

        where_clause = query.whereclause
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[DatabaseProviderIngestionListSchema](
            page_size=limit,
            page_count=math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=[
                DatabaseProviderIngestionListSchema.model_validate(row)
                for row in rows
            ],
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(
        self, database_provider_ingestion_id: UUID, silent=False
    ) -> typing.Optional[DatabaseProviderIngestionItemSchema]:
        """
        Retrieve a DatabaseProviderIngestion instance by id.
        Args:
            database_provider_ingestion_id: The ID of the DatabaseProviderIngestion instance to retrieve.
        Returns:
            DatabaseProviderIngestion: Found instance or None
        """
        database_provider_ingestion = await self._get(
            database_provider_ingestion_id
        )
        if database_provider_ingestion:
            return DatabaseProviderIngestionItemSchema.model_validate(
                database_provider_ingestion
            )
        elif not silent:
            raise ex.EntityNotFoundException(
                "DatabaseProviderIngestion", database_provider_ingestion_id
            )
        else:
            return None

    async def _get(
        self, database_provider_ingestion_id: UUID
    ) -> typing.Optional[DatabaseProviderIngestion]:
        filter_condition = (
            DatabaseProviderIngestion.id == database_provider_ingestion_id
        )
        result = await self.session.execute(
            select(DatabaseProviderIngestion)
            .options(selectinload(DatabaseProviderIngestion.provider))
            .filter(filter_condition)
        )
        return result.scalars().first()
