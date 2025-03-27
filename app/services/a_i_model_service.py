import logging
import math
import typing
from uuid import UUID
from sqlalchemy import asc, desc, and_, func

import app.exceptions as ex
from ..utils.decorators import handle_db_exceptions
from ..utils.models import update_related_collection
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from ..schemas import (
    PaginatedSchema,
    AIModelCreateSchema,
    AIModelUpdateSchema,
    AIModelItemSchema,
    AIModelListSchema,
    AIModelQuerySchema,
)
from ..models import (
    AIModel,
    AIModelAttribute,
    AIModelHyperParameter,
    AIModelResult,
)
from . import BaseService

log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


class AIModelService(BaseService):
    """Service class implementing business logic for
    AIModel entities"""

    def __init__(self, session: AsyncSession):
        super().__init__(AIModel, session)
        self.session = session

    @handle_db_exceptions("Failed to create {}")
    async def add(
        self, a_i_model_data: AIModelCreateSchema
    ) -> AIModelItemSchema:
        """
        Create a new AIModel instance.

        Args:
            a_i_model: The new instance.
        Returns:
            AIModel: Created instance
        """
        exclude = {
            "attributes",
            "hyper_parameters",
            "results",
        }
        a_i_model = AIModel(
            **a_i_model_data.model_dump(exclude_unset=True, exclude=exclude)
        )

        # Update "many" side from one to many when association is a composition
        # Add AIModelAttribute to the AIModel
        if a_i_model_data.attributes:
            for attributes_data in a_i_model_data.attributes:
                new_attributes = AIModelAttribute(
                    **attributes_data.model_dump(exclude_unset=True)
                )
                a_i_model.attributes.append(new_attributes)

        # Add AIModelHyperParameter to the AIModel
        if a_i_model_data.hyper_parameters:
            for hyper_parameters_data in a_i_model_data.hyper_parameters:
                new_hyper_parameters = AIModelHyperParameter(
                    **hyper_parameters_data.model_dump(exclude_unset=True)
                )
                a_i_model.hyper_parameters.append(new_hyper_parameters)

        # Add AIModelResult to the AIModel
        if a_i_model_data.results:
            for results_data in a_i_model_data.results:
                new_results = AIModelResult(
                    **results_data.model_dump(exclude_unset=True)
                )
                a_i_model.results.append(new_results)

        self.session.add(a_i_model)
        await self.session.flush()
        await self.session.refresh(a_i_model)
        return AIModelItemSchema.model_validate(a_i_model)

    @handle_db_exceptions("Failed to delete {}")
    async def delete(
        self, a_i_model_id: typing.Union[UUID, str]
    ) -> typing.Optional[AIModelItemSchema]:
        """
        Delete AIModel instance.
        Args:
            a_i_model_id: The ID of the AIModel instance to delete.
        Returns:
            AIModel: Deleted instance if found or None
        """
        a_i_model = await self._get(a_i_model_id)
        if a_i_model:
            await self.session.delete(a_i_model)
            await self.session.flush()
            return AIModelItemSchema.model_validate(a_i_model)
        return None

    @handle_db_exceptions("Failed to update {}.")
    async def update(
        self,
        a_i_model_id: typing.Union[UUID, str],
        a_i_model_data: typing.Optional[AIModelUpdateSchema],
    ) -> AIModelItemSchema:
        """
        Update a single instance of class AIModel.
        Args:
            a_i_model_id: The ID of the AIModel instance to update.
            a_i_model_data: An object containing the updated fields for the instance.
        Returns:
            AIModel: The updated instance if found, None otheriwse

        """
        a_i_model = await self._get(a_i_model_id)
        if not a_i_model:
            raise ex.EntityNotFoundException("AIModel", a_i_model_id)
        if a_i_model_data is not None:
            for key, value in a_i_model_data.model_dump(
                exclude_unset=True,
                exclude={
                    "attributes",
                    "hyper_parameters",
                    "results",
                },
            ).items():
                setattr(a_i_model, key, value)
            # Update collection of attributes
            if a_i_model_data.attributes:
                deletion_list = update_related_collection(
                    collection=a_i_model.attributes,
                    updates=a_i_model_data.attributes,
                    model_class=AIModelAttribute,
                    parent_id_field="model",
                    parent_id_value=a_i_model_id,
                )
                for to_delete in deletion_list:
                    await self.session.delete(to_delete)
            # Update collection of hyper_parameters
            if a_i_model_data.hyper_parameters:
                deletion_list = update_related_collection(
                    collection=a_i_model.hyper_parameters,
                    updates=a_i_model_data.hyper_parameters,
                    model_class=AIModelHyperParameter,
                    parent_id_field="model",
                    parent_id_value=a_i_model_id,
                )
                for to_delete in deletion_list:
                    await self.session.delete(to_delete)
            # Update collection of results
            if a_i_model_data.results:
                deletion_list = update_related_collection(
                    collection=a_i_model.results,
                    updates=a_i_model_data.results,
                    model_class=AIModelResult,
                    parent_id_field="model",
                    parent_id_value=a_i_model_id,
                )
                for to_delete in deletion_list:
                    await self.session.delete(to_delete)

        await self.session.flush()
        await self.session.refresh(a_i_model)
        return AIModelItemSchema.model_validate(a_i_model)

    @handle_db_exceptions("Failed to retrieve {}")
    async def find(
        self, query_options: AIModelQuerySchema
    ) -> PaginatedSchema[AIModelListSchema]:
        """
        Retrieve a paginated, sorted list of AIModel instances.

        Args:

        Returns:
            List[AIModel]: List of AIModel instances
        """
        page = max(query_options.page, 1)
        limit = min(max(1, query_options.page_size), 100)
        offset = (page - 1) * limit

        query = select(AIModel)
        filter_opts = {
            "query": (
                (
                    AIModel.name,
                    AIModel.display_name,
                    AIModel.description,
                ),
                "ilike",
            ),
        }
        filters = self.get_filters(AIModel, filter_opts, query_options)

        if filters:
            query = query.where(and_(*filters))

        if query_options.sort_by and hasattr(AIModel, query_options.sort_by):
            order_func = asc if query_options.sort_order != "desc" else desc
            query = query.order_by(
                order_func(getattr(AIModel, query_options.sort_by))
            )
        rows = (
            (await self.session.execute(query.offset(offset).limit(limit)))
            .scalars()
            .unique()
            .all()
        )

        count_query = select(func.count()).select_from(AIModel)

        where_clause = query.whereclause
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        total_rows = (await self.session.execute(count_query)).scalar_one()

        return PaginatedSchema[AIModelListSchema](
            page_size=limit,
            page_count=math.ceil(total_rows / limit),
            page=page,
            count=total_rows,
            items=[AIModelListSchema.model_validate(row) for row in rows],
        )

    @handle_db_exceptions("Failed to retrieve {}", status_code=404)
    async def get(
        self, a_i_model_id: typing.Union[UUID, str], silent=False
    ) -> typing.Optional[AIModelItemSchema]:
        """
        Retrieve a AIModel instance by id.
        Args:
            a_i_model_id: The ID of the AIModel instance to retrieve.
        Returns:
            AIModel: Found instance or None
        """
        a_i_model = await self._get(a_i_model_id)
        if a_i_model:
            return AIModelItemSchema.model_validate(a_i_model)
        elif not silent:
            raise ex.EntityNotFoundException("AIModel", a_i_model_id)
        else:
            return None

    async def _get(
        self, a_i_model_id: typing.Union[UUID, str]
    ) -> typing.Optional[AIModel]:
        filter_condition = (
            AIModel.id == a_i_model_id
            if isinstance(a_i_model_id, UUID)
            else AIModel.fully_qualified_name == a_i_model_id
        )
        result = await self.session.execute(
            select(AIModel)
            .options(selectinload(AIModel.attributes))
            .options(selectinload(AIModel.hyper_parameters))
            .options(selectinload(AIModel.results))
            .filter(filter_condition)
        )
        return result.scalars().first()
