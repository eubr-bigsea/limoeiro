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
    UserItemSchema,
    UserListSchema,
    UserCreateSchema,
    UserUpdateSchema,
    UserQuerySchema,
)
from ..models import User
from . import BaseService

log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


class UserService(BaseService):
    """Service class implementing business logic for
    User entities"""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
        self.session = session

    @handle_db_exceptions("Failed to create {}")
    async def add(self, user_data: UserCreateSchema) -> UserItemSchema:
        """
        Create a new User instance.

        Args:
            user: The new instance.
        Returns:
            User: Created instance
        """
        user = User(**user_data.model_dump(exclude_unset=True))
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return UserItemSchema.model_validate(user)

    @handle_db_exceptions("Failed to delete {}")
    async def delete(self, user_id: UUID) -> typing.Optional[UserItemSchema]:
        """
        Delete User instance.
        Args:
            user_id: The ID of the User instance to delete.
        Returns:
            User: Deleted instance if found or None
        """
        user = await self._get(user_id)
        if user:
            await self.session.delete(user)
            await self.session.flush()
            return UserItemSchema.model_validate(user)
        return None

    @handle_db_exceptions("Failed to update {}.")
    async def update(
        self, user_id: UUID, user_data: typing.Optional[UserUpdateSchema]
    ) -> UserItemSchema:
        """
        Update a single instance of class User.
        Args:
            user_id: The ID of the User instance to update.
            user_data: An object containing the updated fields for the instance.
        Returns:
            User: The updated instance if found, None otheriwse

        """
        user = await self._get(user_id)
        if not user:
            raise ex.EntityNotFoundException("User", user_id)
        if user_data is not None:
            for key, value in user_data.model_dump(
                exclude_unset=True, exclude={}
            ).items():
                setattr(user, key, value)

        await self.session.flush()
        await self.session.refresh(user)
        return UserItemSchema.model_validate(user)

    @handle_db_exceptions("Failed to retrieve {}")
    async def find(
        self, query_options: UserQuerySchema
    ) -> PaginatedSchema[UserListSchema]:
        """
        Retrieve a paginated, sorted list of User instances.

        Args:

        Returns:
            List[User]: List of User instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(User)
        filter_opts = {
            "query": (
                (
                    User.name,
                    User.login,
                ),
                "ilike",
            ),
        }
        filters = self.get_filters(User, filter_opts, query_options)

        if filters:
            query = query.where(and_(*filters))

        if query_options.sort_by and hasattr(User, query_options.sort_by):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(User, query_options.sort_by))
            )
        else:
            query = query.order_by(User.name)
        rows = (
            (await self.session.execute(query.offset(offset).limit(limit)))
            .scalars()
            .unique()
            .all()
        )

        count_query = select(func.count()).select_from(User)

        where_clause = query.whereclause
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[UserListSchema](
            page_size=limit,
            page_count=math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=[UserListSchema.model_validate(row) for row in rows],
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(
        self, user_id: UUID, silent=False
    ) -> typing.Optional[UserItemSchema]:
        """
        Retrieve a User instance by id.
        Args:
            user_id: The ID of the User instance to retrieve.
        Returns:
            User: Found instance or None
        """
        user = await self._get(user_id)
        if user:
            return UserItemSchema.model_validate(user)
        elif not silent:
            raise ex.EntityNotFoundException("User", user_id)
        else:
            return None

    async def _get(self, user_id: UUID) -> typing.Optional[User]:
        filter_condition = User.id == user_id
        result = await self.session.execute(
            select(User).filter(filter_condition)
        )
        return result.scalars().first()
