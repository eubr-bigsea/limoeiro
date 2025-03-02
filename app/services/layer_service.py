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
    LayerCreateSchema,
    LayerUpdateSchema,
    LayerItemSchema,
    LayerListSchema,
    LayerQuerySchema,
)
from ..models import Layer
from . import BaseService

log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


class LayerService(BaseService):
    """Service class implementing business logic for
    Layer entities"""

    def __init__(self, session: AsyncSession):
        super().__init__(Layer)
        self.session = session

    async def _get(self, layer_id: UUID) -> typing.Optional[Layer]:
        result = await self.session.execute(
            select(Layer).filter(Layer.id == layer_id)
        )
        return result.scalars().first()

    @handle_db_exceptions("Failed to create {}")
    async def add(self, layer_data: LayerCreateSchema) -> LayerItemSchema:
        """
        Create a new Layer instance.

        Args:
            layer: The new instance.
        Returns:
            Layer: Created instance
        """
        layer = Layer(**layer_data.model_dump(exclude_unset=True))
        self.session.add(layer)
        await self.session.commit()
        await self.session.refresh(layer)
        return LayerItemSchema.model_validate(layer)

    @handle_db_exceptions("Failed to delete {}")
    async def delete(self, layer_id: UUID) -> typing.Optional[LayerItemSchema]:
        """
        Delete Layer instance.
        Args:
            layer_id: The ID of the Layer instance to delete.
        Returns:
            Layer: Deleted instance if found or None
        """
        layer = await self._get(layer_id)
        if layer:
            await self.session.delete(layer)
            await self.session.commit()
            return LayerItemSchema.model_validate(layer)
        return None

    @handle_db_exceptions("Failed to update {}.")
    async def update(
        self, layer_id: UUID, layer_data: typing.Optional[LayerUpdateSchema]
    ) -> LayerItemSchema:
        """
        Update a single instance of class Layer.
        Args:
            layer_id: The ID of the Layer instance to update.
            layer_data: An object containing the updated fields for the instance.
        Returns:
            Layer: The updated instance if found, None otheriwse

        """
        layer = await self._get(layer_id)
        if not layer:
            raise ex.EntityNotFoundException("{cls_name}", layer_id)
        if layer_data is not None:
            for key, value in layer_data.model_dump(
                exclude_unset=True, exclude={}
            ).items():
                setattr(layer, key, value)

        await self.session.commit()
        await self.session.refresh(layer)
        return LayerItemSchema.model_validate(layer)

    @handle_db_exceptions("Failed to retrieve {}")
    async def find(
        self, query_options: LayerQuerySchema
    ) -> PaginatedSchema[LayerListSchema]:
        """
        Retrieve a paginated, sorted list of Layer instances.

        Args:

        Returns:
            List[Layer]: List of Layer instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(Layer)
        filter_opts = {
            "query": (
                (
                    Layer.name,
                    Layer.description,
                ),
                "ilike",
            ),
        }
        filters = self.get_filters(Layer, filter_opts, query_options)

        if filters:
            query = query.where(and_(*filters))

        if query_options.sort_by and hasattr(Layer, query_options.sort_by):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(Layer, query_options.sort_by))
            )
        # ???
        rows = list(
            (await self.session.execute(query.offset(offset).limit(limit)))
            .scalars()
            .unique()
            .all()
        )

        count_query = select(func.count()).select_from(Layer)

        where_clause = query.whereclause
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[LayerListSchema](
            page_size=limit,
            page_count=math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=[LayerListSchema.model_validate(row) for row in rows],
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(self, layer_id: UUID) -> LayerItemSchema:
        """
        Retrieve a Layer instance by id.
        Args:
            layer_id: The ID of the Layer instance to retrieve.
        Returns:
            Layer: Found instance or None
        """
        return LayerItemSchema.model_validate(await self._get(layer_id))
