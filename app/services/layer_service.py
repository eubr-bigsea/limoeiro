import logging
import math
from uuid import UUID
from sqlalchemy import asc, desc, and_, func
from ..utils.decorators import handle_db_exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..schemas import (
    PaginatedSchema,
    LayerCreateSchema,
    LayerQuerySchema,
)
from ..models import Layer
from . import BaseService
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*

class LayerService(BaseService):
    """ Service class implementing business logic for
    Layer entities"""
    def __init__(self, session: AsyncSession ):
        super().__init__(Layer)
        self.session = session

    @handle_db_exceptions("Failed to create {}")
    async def add(
        self, layer_data: LayerCreateSchema
    ) -> Layer:
        """
        Create a new Layer instance.

        Args:
            layer: The new instance.
        Returns:
            Layer: Created instance
        """
        layer = Layer(**layer_data.model_dump(
            exclude_unset=True))
        self.session.add(layer)
        await self.session.commit()
        await self.session.refresh(layer)
        return layer

    @handle_db_exceptions("Failed to delete {}")
    async def delete(self, layer_id: UUID) -> Layer:
        """
        Delete Layer instance.
        Args:
            layer_id: The ID of the Layer instance to delete.
        Returns:
            Layer: Deleted instance if found or None
        """
        layer = await self.get(layer_id)
        if layer:
            await self.session.delete(layer)
            await self.session.commit()
        return layer

    @handle_db_exceptions("Failed to update {}")
    async def update(self,
        layer_id: UUID,
        layer_data: Layer) -> Layer:
        """
        Update a single instance of class Layer.
        Args:
            layer_id: The ID of the Layer instance to update.
            layer_data: An object containing the updated fields for the instance.
        Returns:
            Layer: The updated instance if found, None otheriwse

        """
        layer = await self.get(layer_id)
        if not layer:
            return None
        for key, value in layer_data.model_dump(
            exclude_unset=True).items():
            setattr(layer, key, value)
        await self.session.commit()
        await self.session.refresh(layer)

        return layer
    @handle_db_exceptions("Failed to retrieve {}")
    async def find(self,
        query_options: LayerQuerySchema
    ) -> PaginatedSchema[Layer]:
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
            "query": ((
               Layer.name,
               Layer.display_name,
               Layer.description,
            ), "ilike"),
        }
        filters = self.get_filters(Layer, filter_opts, query_options)

        if filters:
            query = query.where(and_(*filters))

        if (
            query_options.sort_by and
                hasattr(Layer, query_options.sort_by)
        ):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(Layer, query_options.sort_by)))
        rows = (
            await self.session.execute(query.offset(offset).limit(limit))
        ).scalars().unique().all()

        count_query = select(func.count()).select_from(
            query.selectable.with_only_columns(Layer.id)
        )
        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[Layer](
            page_size=limit,
            page_count = math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=rows,
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(self, layer_id: UUID) -> Layer:
        """
        Retrieve a Layer instance by id.
        Args:
            layer_id: The ID of the Layer instance to retrieve.
        Returns:
            Layer: Found instance or None
        """
        result = await self.session.execute(
            select(Layer)
            .filter(Layer.id == layer_id))
        return result.scalars().first()
