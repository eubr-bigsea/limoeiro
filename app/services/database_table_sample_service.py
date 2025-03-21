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
    DatabaseTableSampleCreateSchema,
    DatabaseTableSampleUpdateSchema,
    DatabaseTableSampleItemSchema,
    DatabaseTableSampleListSchema,
    DatabaseTableSampleQuerySchema,
)
from ..models import DatabaseTableSample
from . import BaseService

log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


class DatabaseTableSampleService(BaseService):
    """Service class implementing business logic for
    DatabaseTableSample entities"""

    def __init__(self, session: AsyncSession):
        super().__init__(DatabaseTableSample, session)
        self.session = session

    @handle_db_exceptions("Failed to create {}")
    async def add(
        self, database_table_sample_data: DatabaseTableSampleCreateSchema
    ) -> DatabaseTableSampleItemSchema:
        """
        Create a new DatabaseTableSample instance.

        Args:
            database_table_sample: The new instance.
        Returns:
            DatabaseTableSample: Created instance
        """
        database_table_sample = DatabaseTableSample(
            **database_table_sample_data.model_dump(exclude_unset=True)
        )
        self.session.add(database_table_sample)
        await self.session.commit()
        await self.session.refresh(database_table_sample)
        return DatabaseTableSampleItemSchema.model_validate(
            database_table_sample
        )

    @handle_db_exceptions("Failed to delete {}")
    async def delete(
        self, database_table_sample_id: UUID
    ) -> typing.Optional[DatabaseTableSampleItemSchema]:
        """
        Delete DatabaseTableSample instance.
        Args:
            database_table_sample_id: The ID of the DatabaseTableSample instance to delete.
        Returns:
            DatabaseTableSample: Deleted instance if found or None
        """
        database_table_sample = await self._get(database_table_sample_id)
        if database_table_sample:
            await self.session.delete(database_table_sample)
            await self.session.commit()
            return DatabaseTableSampleItemSchema.model_validate(
                database_table_sample
            )
        return None

    @handle_db_exceptions("Failed to update {}.")
    async def update(
        self,
        database_table_sample_id: UUID,
        database_table_sample_data: typing.Optional[
            DatabaseTableSampleUpdateSchema
        ],
    ) -> DatabaseTableSampleItemSchema:
        """
        Update a single instance of class DatabaseTableSample.
        Args:
            database_table_sample_id: The ID of the DatabaseTableSample instance to update.
            database_table_sample_data: An object containing the updated fields for the instance.
        Returns:
            DatabaseTableSample: The updated instance if found, None otheriwse

        """
        database_table_sample = await self._get(database_table_sample_id)
        if not database_table_sample:
            raise ex.EntityNotFoundException(
                "DatabaseTableSample", database_table_sample_id
            )
        if database_table_sample_data is not None:
            for key, value in database_table_sample_data.model_dump(
                exclude_unset=True, exclude={}
            ).items():
                setattr(database_table_sample, key, value)

        await self.session.commit()
        await self.session.refresh(database_table_sample)
        return DatabaseTableSampleItemSchema.model_validate(
            database_table_sample
        )

    @handle_db_exceptions("Failed to retrieve {}")
    async def find(
        self, query_options: DatabaseTableSampleQuerySchema
    ) -> PaginatedSchema[DatabaseTableSampleListSchema]:
        """
        Retrieve a paginated, sorted list of DatabaseTableSample instances.

        Args:

        Returns:
            List[DatabaseTableSample]: List of DatabaseTableSample instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(DatabaseTableSample)
        filter_opts = {
            "database_table_id": (
                DatabaseTableSample.database_table_id,
                "__eq__",
            ),
        }
        filters = self.get_filters(
            DatabaseTableSample, filter_opts, query_options
        )

        if filters:
            query = query.where(and_(*filters))

        if query_options.sort_by and hasattr(
            DatabaseTableSample, query_options.sort_by
        ):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(DatabaseTableSample, query_options.sort_by))
            )
        rows = (
            (await self.session.execute(query.offset(offset).limit(limit)))
            .scalars()
            .unique()
            .all()
        )

        count_query = select(func.count()).select_from(DatabaseTableSample)

        where_clause = query.whereclause
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[DatabaseTableSampleListSchema](
            page_size=limit,
            page_count=math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=[
                DatabaseTableSampleListSchema.model_validate(row) for row in rows
            ],
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(
        self, database_table_sample_id: UUID
    ) -> typing.Optional[DatabaseTableSampleItemSchema]:
        """
        Retrieve a DatabaseTableSample instance by id.
        Args:
            database_table_sample_id: The ID of the DatabaseTableSample instance to retrieve.
        Returns:
            DatabaseTableSample: Found instance or None
        """
        database_table_sample = await self._get(database_table_sample_id)
        if database_table_sample:
            return DatabaseTableSampleItemSchema.model_validate(
                database_table_sample
            )
        else:
            raise ex.EntityNotFoundException(
                "DatabaseTableSample", database_table_sample_id
            )

    async def _get(
        self, database_table_sample_id: UUID
    ) -> typing.Optional[DatabaseTableSample]:
        filter_condition = DatabaseTableSample.id == database_table_sample_id
        result = await self.session.execute(
            select(DatabaseTableSample)
            .options(selectinload(DatabaseTableSample.database_table))
            .filter(filter_condition)
        )
        return result.scalars().first()
