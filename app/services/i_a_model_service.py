import logging
import math
from uuid import UUID
from sqlalchemy import asc, desc, and_, func
from ..utils.decorators import handle_db_exceptions
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from ..schemas import (
    PaginatedSchema,
    IAModelCreateSchema,
    IAModelQuerySchema,
)
from ..models import IAModel, IAModelAttribute, IAModelHyperParameter, IAModelResult
from . import BaseService
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*

class IAModelService(BaseService):
    """ Service class implementing business logic for
    IAModel entities"""
    def __init__(self, session: AsyncSession ):
        super().__init__(IAModel)
        self.session = session

    @handle_db_exceptions("Failed to create {}")
    async def add(
        self, i_a_model_data: IAModelCreateSchema
    ) -> IAModel:
        """
        Create a new IAModel instance.

        Args:
            i_a_model: The new instance.
        Returns:
            IAModel: Created instance
        """
        exclude = { "attributes", "hyper_parameters", "results", }
        i_a_model = IAModel(**i_a_model_data.model_dump(
            exclude_unset=True, exclude=exclude))

        # Update "many" side from one to many when association is a composition
        # Add IAModelAttribute to the IAModel
        for attributes_data in i_a_model_data.attributes:
            new_attributes = IAModelAttribute(**attributes_data.model_dump(
                exclude_unset=True))
            i_a_model.attributes.append(new_attributes)
        
        # Add IAModelHyperParameter to the IAModel
        for hyper_parameters_data in i_a_model_data.hyper_parameters:
            new_hyper_parameters = IAModelHyperParameter(**hyper_parameters_data.model_dump(
                exclude_unset=True))
            i_a_model.hyper_parameters.append(new_hyper_parameters)
        
        # Add IAModelResult to the IAModel
        for results_data in i_a_model_data.results:
            new_results = IAModelResult(**results_data.model_dump(
                exclude_unset=True))
            i_a_model.results.append(new_results)
        
        self.session.add(i_a_model)
        await self.session.commit()
        await self.session.refresh(i_a_model)
        return i_a_model

    @handle_db_exceptions("Failed to delete {}")
    async def delete(self, i_a_model_id: UUID) -> IAModel:
        """
        Delete IAModel instance.
        Args:
            i_a_model_id: The ID of the IAModel instance to delete.
        Returns:
            IAModel: Deleted instance if found or None
        """
        i_a_model = await self.get(i_a_model_id)
        if i_a_model:
            await self.session.delete(i_a_model)
            await self.session.commit()
        return i_a_model

    @handle_db_exceptions("Failed to update {}")
    async def update(self,
        i_a_model_id: UUID,
        i_a_model_data: IAModel) -> IAModel:
        """
        Update a single instance of class IAModel.
        Args:
            i_a_model_id: The ID of the IAModel instance to update.
            i_a_model_data: An object containing the updated fields for the instance.
        Returns:
            IAModel: The updated instance if found, None otheriwse

        """
        i_a_model = await self.get(i_a_model_id)
        if not i_a_model:
            return None
        for key, value in i_a_model_data.model_dump(
            exclude_unset=True).items():
            setattr(i_a_model, key, value)
        await self.session.commit()
        await self.session.refresh(i_a_model)

        return i_a_model
    @handle_db_exceptions("Failed to retrieve {}")
    async def find(self,
        query_options: IAModelQuerySchema
    ) -> PaginatedSchema[IAModel]:
        """
        Retrieve a paginated, sorted list of IAModel instances.

        Args:

        Returns:
            List[IAModel]: List of IAModel instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(IAModel)
        filter_opts = {
            "query": ((
               IAModel.name,
               IAModel.display_name,
               IAModel.description,
            ), "ilike"),
        }
        filters = self.get_filters(IAModel, filter_opts, query_options)

        if filters:
            query = query.where(and_(*filters))

        if (
            query_options.sort_by and
                hasattr(IAModel, query_options.sort_by)
        ):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(IAModel, query_options.sort_by)))
        rows = (
            await self.session.execute(query.offset(offset).limit(limit))
        ).scalars().unique().all()

        count_query = select(func.count()).select_from(
            query.selectable.with_only_columns(IAModel.id)
        )
        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[IAModel](
            page_size=limit,
            page_count = math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=rows,
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(self, i_a_model_id: UUID) -> IAModel:
        """
        Retrieve a IAModel instance by id.
        Args:
            i_a_model_id: The ID of the IAModel instance to retrieve.
        Returns:
            IAModel: Found instance or None
        """
        result = await self.session.execute(
            select(IAModel)
            .options(selectinload(IAModel.domain))
            .options(selectinload(IAModel.attributes))
            .options(selectinload(IAModel.hyper_parameters))
            .options(selectinload(IAModel.results))
            .filter(IAModel.id == i_a_model_id))
        return result.scalars().first()
