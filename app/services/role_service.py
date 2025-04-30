from http import HTTPStatus
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
    RoleItemSchema,
    RoleListSchema,
    RoleCreateSchema,
    RoleUpdateSchema,
    RoleQuerySchema,
)
from ..models import Permission, Role, User
from . import BaseService

log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


class RoleService(BaseService):
    """Service class implementing business logic for
    Role entities"""

    def __init__(self, session: AsyncSession):
        super().__init__(Role, session)
        self.session = session

    @handle_db_exceptions("Failed to create {}")
    async def add(self, role_data: RoleCreateSchema) -> RoleItemSchema:
        """
        Create a new Role instance.

        Args:
            role: The new instance.
        Returns:
            Role: Created instance
        """
        if role_data is not None:
            role = Role(
                **role_data.model_dump(
                    exclude_unset=True, exclude={"permissions", "users"}
                )
            )
            for key, value in role_data.model_dump(
                exclude_unset=True, exclude={}
            ).items():
                if key not in ("permissions", "users"):
                    setattr(role, key, value)

            await self.update_related_collections(role, role_data)

        self.session.add(role)
        await self.session.flush()
        await self.session.refresh(role)
        return RoleItemSchema.model_validate(role)

    @handle_db_exceptions("Failed to delete {}")
    async def delete(self, role_id: UUID) -> typing.Optional[RoleItemSchema]:
        """
        Delete Role instance.
        Args:
            role_id: The ID of the Role instance to delete.
        Returns:
            Role: Deleted instance if found or None
        """
        role = await self._get(role_id)
        if role:
            await self.session.delete(role)
            await self.session.flush()
            return RoleItemSchema.model_validate(role)
        return None

    @handle_db_exceptions("Failed to update {}.")
    async def update(
        self, role_id: UUID, role_data: typing.Optional[RoleUpdateSchema]
    ) -> RoleItemSchema:
        """
        Update a single instance of class Role.
        Args:
            role_id: The ID of the Role instance to update.
            role_data: An object containing the updated fields for the instance.
        Returns:
            Role: The updated instance if found, None otheriwse

        """
        role = await self._get(role_id)
        if not role:
            raise ex.EntityNotFoundException("Role", role_id)
        if role_data is not None:
            for key, value in role_data.model_dump(
                exclude_unset=True, exclude={}
            ).items():
                if key not in ("permissions", "users"):
                    setattr(role, key, value)

            await self.update_related_collections(role, role_data)

        await self.session.flush()
        await self.session.refresh(role)
        return RoleItemSchema.model_validate(role)

    async def update_related_collections(
        self,
        role: Role,
        role_data: typing.Union[RoleUpdateSchema, RoleCreateSchema],
    ):
        """
        Update related collections for a Role instance.
        """
        # Generalize handling for related collections
        for field, klass in zip(("permissions", "users"), (Permission, User)):
            ids = getattr(role_data, field, None)
            # Get all related entities matching the provided keys
            if ids:
                related_entities = (
                    (
                        await self.session.execute(
                            select(klass).where(klass.id.in_(ids))
                        )
                    )
                    .scalars()
                    .all()
                )

                # Verify all requested entities exist
                found_keys = {entity.id for entity in related_entities}
                missing_keys = set(ids) - found_keys

                if missing_keys:
                    # Raise error if any keys don't exist
                    raise ex.EntityNotFoundException(
                        entity_type=klass.__name__,
                        entity_id=", ".join(missing_keys),
                        status_code=HTTPStatus.BAD_REQUEST,
                    )

                # Replace all related entities with the new set
                setattr(role, field, related_entities)
            else:
                # Clear the collection if no IDs are provided
                setattr(role, field, [])

    @handle_db_exceptions("Failed to retrieve {}")
    async def find(
        self, query_options: RoleQuerySchema
    ) -> PaginatedSchema[RoleListSchema]:
        """
        Retrieve a paginated, sorted list of Role instances.

        Args:

        Returns:
            List[Role]: List of Role instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(Role)
        filter_opts = {
            "query": (
                (
                    Role.name,
                    Role.description,
                ),
                "ilike",
            ),
        }
        filters = self.get_filters(Role, filter_opts, query_options)

        if filters:
            query = query.where(and_(*filters))

        if query_options.sort_by and hasattr(Role, query_options.sort_by):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(Role, query_options.sort_by))
            )
        else:
            query = query.order_by(Role.name)
        rows = (
            (await self.session.execute(query.offset(offset).limit(limit)))
            .scalars()
            .unique()
            .all()
        )

        count_query = select(func.count()).select_from(Role)

        where_clause = query.whereclause
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[RoleListSchema](
            page_size=limit,
            page_count=math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=[RoleListSchema.model_validate(row) for row in rows],
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(
        self, role_id: UUID, silent=False
    ) -> typing.Optional[RoleItemSchema]:
        """
        Retrieve a Role instance by id.
        Args:
            role_id: The ID of the Role instance to retrieve.
        Returns:
            Role: Found instance or None
        """
        role = await self._get(role_id)
        if role:
            return RoleItemSchema.model_validate(role)
        elif not silent:
            raise ex.EntityNotFoundException("Role", role_id)
        else:
            return None

    async def _get(self, role_id: UUID) -> typing.Optional[Role]:
        filter_condition = Role.id == role_id
        result = await self.session.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .options(selectinload(Role.users))
            .filter(filter_condition)
        )
        return result.scalars().first()
