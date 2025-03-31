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
    ContactCreateSchema,
    ContactUpdateSchema,
    ContactItemSchema,
    ContactListSchema,
    ContactQuerySchema,
)
from ..models import Contact
from . import BaseService

log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


class ContactService(BaseService):
    """Service class implementing business logic for
    Contact entities"""

    def __init__(self, session: AsyncSession):
        super().__init__(Contact, session)
        self.session = session

    @handle_db_exceptions("Failed to create {}")
    async def add(self, contact_data: ContactCreateSchema) -> ContactItemSchema:
        """
        Create a new Contact instance.

        Args:
            contact: The new instance.
        Returns:
            Contact: Created instance
        """
        contact = Contact(**contact_data.model_dump(exclude_unset=True))
        self.session.add(contact)
        await self.session.flush()
        await self.session.refresh(contact)
        return ContactItemSchema.model_validate(contact)

    @handle_db_exceptions("Failed to delete {}")
    async def delete(
        self, contact_id: UUID
    ) -> typing.Optional[ContactItemSchema]:
        """
        Delete Contact instance.
        Args:
            contact_id: The ID of the Contact instance to delete.
        Returns:
            Contact: Deleted instance if found or None
        """
        contact = await self._get(contact_id)
        if contact:
            await self.session.delete(contact)
            await self.session.flush()
            return ContactItemSchema.model_validate(contact)
        return None

    @handle_db_exceptions("Failed to update {}.")
    async def update(
        self,
        contact_id: UUID,
        contact_data: typing.Optional[ContactUpdateSchema],
    ) -> ContactItemSchema:
        """
        Update a single instance of class Contact.
        Args:
            contact_id: The ID of the Contact instance to update.
            contact_data: An object containing the updated fields for the instance.
        Returns:
            Contact: The updated instance if found, None otheriwse

        """
        contact = await self._get(contact_id)
        if not contact:
            raise ex.EntityNotFoundException("Contact", contact_id)
        if contact_data is not None:
            for key, value in contact_data.model_dump(
                exclude_unset=True, exclude={}
            ).items():
                setattr(contact, key, value)

        await self.session.flush()
        await self.session.refresh(contact)
        return ContactItemSchema.model_validate(contact)

    @handle_db_exceptions("Failed to retrieve {}")
    async def find(
        self, query_options: ContactQuerySchema
    ) -> PaginatedSchema[ContactListSchema]:
        """
        Retrieve a paginated, sorted list of Contact instances.

        Args:

        Returns:
            List[Contact]: List of Contact instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(Contact)
        filter_opts = {
            "query": (
                (
                    Contact.name,
                    Contact.email,
                    Contact.description,
                ),
                "ilike",
            ),
        }
        filters = self.get_filters(Contact, filter_opts, query_options)

        if filters:
            query = query.where(and_(*filters))

        if query_options.sort_by and hasattr(Contact, query_options.sort_by):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(Contact, query_options.sort_by))
            )
        else:
            query = query.order_by(Contact.name)
        rows = (
            (await self.session.execute(query.offset(offset).limit(limit)))
            .scalars()
            .unique()
            .all()
        )

        count_query = select(func.count()).select_from(Contact)

        where_clause = query.whereclause
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[ContactListSchema](
            page_size=limit,
            page_count=math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=[ContactListSchema.model_validate(row) for row in rows],
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(
        self, contact_id: UUID, silent=False
    ) -> typing.Optional[ContactItemSchema]:
        """
        Retrieve a Contact instance by id.
        Args:
            contact_id: The ID of the Contact instance to retrieve.
        Returns:
            Contact: Found instance or None
        """
        contact = await self._get(contact_id)
        if contact:
            return ContactItemSchema.model_validate(contact)
        elif not silent:
            raise ex.EntityNotFoundException("Contact", contact_id)
        else:
            return None

    async def _get(self, contact_id: UUID) -> typing.Optional[Contact]:
        filter_condition = Contact.id == contact_id
        result = await self.session.execute(
            select(Contact).filter(filter_condition)
        )
        return result.scalars().first()
