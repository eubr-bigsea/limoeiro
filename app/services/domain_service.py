import logging
import math
from uuid import UUID
from sqlalchemy import asc, desc, and_, func
from ..utils.decorators import handle_db_exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..schemas import (
    PaginatedSchema,
    DomainCreateSchema,
    DomainQuerySchema,
)
from ..models import Domain
from . import BaseService
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*

class DomainService(BaseService):
    """ Service class implementing business logic for
    Domain entities"""
    def __init__(self, session: AsyncSession ):
        super().__init__(Domain)
        self.session = session

    @handle_db_exceptions("Failed to create {}")
    async def add(
        self, domain_data: DomainCreateSchema
    ) -> Domain:
        """
        Create a new Domain instance.

        Args:
            domain: The new instance.
        Returns:
            Domain: Created instance
        """
        domain = Domain(**domain_data.model_dump(
            exclude_unset=True))
        self.session.add(domain)
        await self.session.commit()
        await self.session.refresh(domain)
        return domain

    @handle_db_exceptions("Failed to delete {}")
    async def delete(self, domain_id: UUID) -> Domain:
        """
        Delete Domain instance.
        Args:
            domain_id: The ID of the Domain instance to delete.
        Returns:
            Domain: Deleted instance if found or None
        """
        domain = await self.get(domain_id)
        if domain:
            await self.session.delete(domain)
            await self.session.commit()
        return domain

    @handle_db_exceptions("Failed to update {}")
    async def update(self,
        domain_id: UUID,
        domain_data: Domain) -> Domain:
        """
        Update a single instance of class Domain.
        Args:
            domain_id: The ID of the Domain instance to update.
            domain_data: An object containing the updated fields for the instance.
        Returns:
            Domain: The updated instance if found, None otheriwse

        """
        domain = await self.get(domain_id)
        if not domain:
            return None
        for key, value in domain_data.model_dump(
            exclude_unset=True).items():
            setattr(domain, key, value)
        await self.session.commit()
        await self.session.refresh(domain)

        return domain
    @handle_db_exceptions("Failed to retrieve {}")
    async def find(self,
        query_options: DomainQuerySchema
    ) -> PaginatedSchema[Domain]:
        """
        Retrieve a paginated, sorted list of Domain instances.

        Args:

        Returns:
            List[Domain]: List of Domain instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(Domain)
        filter_opts = {
            "query": ((
               Domain.name,
               Domain.description,
            ), "ilike"),
        }
        filters = self.get_filters(Domain, filter_opts, query_options)

        if filters:
            query = query.where(and_(*filters))

        if (
            query_options.sort_by and
                hasattr(Domain, query_options.sort_by)
        ):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(Domain, query_options.sort_by)))
        rows = (
            await self.session.execute(query.offset(offset).limit(limit))
        ).scalars().unique().all()

        count_query = select(func.count()).select_from(
            query.selectable.with_only_columns(Domain.id)
        )
        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[Domain](
            page_size=limit,
            page_count = math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=rows,
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(self, domain_id: UUID) -> Domain:
        """
        Retrieve a Domain instance by id.
        Args:
            domain_id: The ID of the Domain instance to retrieve.
        Returns:
            Domain: Found instance or None
        """
        result = await self.session.execute(
            select(Domain)
            .filter(Domain.id == domain_id))
        return result.scalars().first()
