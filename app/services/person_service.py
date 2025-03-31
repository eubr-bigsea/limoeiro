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
    PersonCreateSchema,
    PersonUpdateSchema,
    PersonItemSchema,
    PersonListSchema,
    PersonQuerySchema,
)
from ..models import Person
from . import BaseService

log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


class PersonService(BaseService):
    """Service class implementing business logic for
    Person entities"""

    def __init__(self, session: AsyncSession):
        super().__init__(Person, session)
        self.session = session

    @handle_db_exceptions("Failed to create {}")
    async def add(self, person_data: PersonCreateSchema) -> PersonItemSchema:
        """
        Create a new Person instance.

        Args:
            person: The new instance.
        Returns:
            Person: Created instance
        """
        person = Person(**person_data.model_dump(exclude_unset=True))
        self.session.add(person)
        await self.session.flush()
        await self.session.refresh(person)
        return PersonItemSchema.model_validate(person)

    @handle_db_exceptions("Failed to delete {}")
    async def delete(self, person_id: UUID) -> typing.Optional[PersonItemSchema]:
        """
        Delete Person instance.
        Args:
            person_id: The ID of the Person instance to delete.
        Returns:
            Person: Deleted instance if found or None
        """
        person = await self._get(person_id)
        if person:
            await self.session.delete(person)
            await self.session.flush()
            return PersonItemSchema.model_validate(person)
        return None

    @handle_db_exceptions("Failed to update {}.")
    async def update(
        self, person_id: UUID, person_data: typing.Optional[PersonUpdateSchema]
    ) -> PersonItemSchema:
        """
        Update a single instance of class Person.
        Args:
            person_id: The ID of the Person instance to update.
            person_data: An object containing the updated fields for the instance.
        Returns:
            Person: The updated instance if found, None otheriwse

        """
        person = await self._get(person_id)
        if not person:
            raise ex.EntityNotFoundException("Person", person_id)
        if person_data is not None:
            for key, value in person_data.model_dump(
                exclude_unset=True, exclude={}
            ).items():
                setattr(person, key, value)

        await self.session.flush()
        await self.session.refresh(person)
        return PersonItemSchema.model_validate(person)

    @handle_db_exceptions("Failed to retrieve {}")
    async def find(
        self, query_options: PersonQuerySchema
    ) -> PaginatedSchema[PersonListSchema]:
        """
        Retrieve a paginated, sorted list of Person instances.

        Args:

        Returns:
            List[Person]: List of Person instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(Person)
        filter_opts = {
            "query": (
                (
                    Person.name,
                    Person.description,
                ),
                "ilike",
            ),
        }
        filters = self.get_filters(Person, filter_opts, query_options)

        if filters:
            query = query.where(and_(*filters))

        if query_options.sort_by and hasattr(Person, query_options.sort_by):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(Person, query_options.sort_by))
            )
        else:
            query = query.order_by(Person.name)
        rows = (
            (await self.session.execute(query.offset(offset).limit(limit)))
            .scalars()
            .unique()
            .all()
        )

        count_query = select(func.count()).select_from(Person)

        where_clause = query.whereclause
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[PersonListSchema](
            page_size=limit,
            page_count=math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=[PersonListSchema.model_validate(row) for row in rows],
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(
        self, person_id: UUID, silent=False
    ) -> typing.Optional[PersonItemSchema]:
        """
        Retrieve a Person instance by id.
        Args:
            person_id: The ID of the Person instance to retrieve.
        Returns:
            Person: Found instance or None
        """
        person = await self._get(person_id)
        if person:
            return PersonItemSchema.model_validate(person)
        elif not silent:
            raise ex.EntityNotFoundException("Person", person_id)
        else:
            return None

    async def _get(self, person_id: UUID) -> typing.Optional[Person]:
        filter_condition = Person.id == person_id
        result = await self.session.execute(
            select(Person)
            .options(selectinload(Person.user))
            .filter(filter_condition)
        )
        return result.scalars().first()
