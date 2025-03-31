import logging
import math
import typing
from uuid import UUID
from sqlalchemy import asc, desc, and_, func

import app.exceptions as ex
from ..utils.decorators import handle_db_exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..schemas import (
    PaginatedSchema,
    CompanyCreateSchema,
    CompanyUpdateSchema,
    CompanyItemSchema,
    CompanyListSchema,
    CompanyQuerySchema,
)
from ..models import Company
from . import BaseService

log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


class CompanyService(BaseService):
    """Service class implementing business logic for
    Company entities"""

    def __init__(self, session: AsyncSession):
        super().__init__(Company, session)
        self.session = session

    @handle_db_exceptions("Failed to create {}")
    async def add(self, company_data: CompanyCreateSchema) -> CompanyItemSchema:
        """
        Create a new Company instance.

        Args:
            company: The new instance.
        Returns:
            Company: Created instance
        """
        company = Company(**company_data.model_dump(exclude_unset=True))
        self.session.add(company)
        await self.session.flush()
        await self.session.refresh(company)
        return CompanyItemSchema.model_validate(company)

    @handle_db_exceptions("Failed to delete {}")
    async def delete(
        self, company_id: UUID
    ) -> typing.Optional[CompanyItemSchema]:
        """
        Delete Company instance.
        Args:
            company_id: The ID of the Company instance to delete.
        Returns:
            Company: Deleted instance if found or None
        """
        company = await self._get(company_id)
        if company:
            await self.session.delete(company)
            await self.session.flush()
            return CompanyItemSchema.model_validate(company)
        return None

    @handle_db_exceptions("Failed to update {}.")
    async def update(
        self,
        company_id: UUID,
        company_data: typing.Optional[CompanyUpdateSchema],
    ) -> CompanyItemSchema:
        """
        Update a single instance of class Company.
        Args:
            company_id: The ID of the Company instance to update.
            company_data: An object containing the updated fields for the instance.
        Returns:
            Company: The updated instance if found, None otheriwse

        """
        company = await self._get(company_id)
        if not company:
            raise ex.EntityNotFoundException("Company", company_id)
        if company_data is not None:
            for key, value in company_data.model_dump(
                exclude_unset=True, exclude={}
            ).items():
                setattr(company, key, value)

        await self.session.flush()
        await self.session.refresh(company)
        return CompanyItemSchema.model_validate(company)

    @handle_db_exceptions("Failed to retrieve {}")
    async def find(
        self, query_options: CompanyQuerySchema
    ) -> PaginatedSchema[CompanyListSchema]:
        """
        Retrieve a paginated, sorted list of Company instances.

        Args:

        Returns:
            List[Company]: List of Company instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(Company)
        filter_opts = {
            "query": (
                (
                    Company.name,
                    Company.description,
                ),
                "ilike",
            ),
        }
        filters = self.get_filters(Company, filter_opts, query_options)

        if filters:
            query = query.where(and_(*filters))

        if query_options.sort_by and hasattr(Company, query_options.sort_by):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(Company, query_options.sort_by))
            )
        else:
            query = query.order_by(Company.name)
        rows = (
            (await self.session.execute(query.offset(offset).limit(limit)))
            .scalars()
            .unique()
            .all()
        )

        count_query = select(func.count()).select_from(Company)

        where_clause = query.whereclause
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[CompanyListSchema](
            page_size=limit,
            page_count=math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=[CompanyListSchema.model_validate(row) for row in rows],
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(
        self, company_id: UUID, silent=False
    ) -> typing.Optional[CompanyItemSchema]:
        """
        Retrieve a Company instance by id.
        Args:
            company_id: The ID of the Company instance to retrieve.
        Returns:
            Company: Found instance or None
        """
        company = await self._get(company_id)
        if company:
            return CompanyItemSchema.model_validate(company)
        elif not silent:
            raise ex.EntityNotFoundException("Company", company_id)
        else:
            return None

    async def _get(self, company_id: UUID) -> typing.Optional[Company]:
        filter_condition = Company.id == company_id
        result = await self.session.execute(
            select(Company).filter(filter_condition)
        )
        return result.scalars().first()
