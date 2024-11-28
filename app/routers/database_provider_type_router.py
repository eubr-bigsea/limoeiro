import logging
import typing
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends

from ..schemas import (
    BaseQuerySchema,
    PaginatedSchema,
    DatabaseProviderTypeItemSchema,
    DatabaseProviderTypeListSchema,
)
from ..services.database_provider_type_service import DatabaseProviderTypeService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*

@router.get("/database-provider-types/{database_provider_type_id}",
    tags=["DatabaseProviderType"],
    response_model=DatabaseProviderTypeItemSchema,
    response_model_exclude_none=False)
async def get_database_provider_type(database_provider_type_id: str,
    db: AsyncSession = Depends(get_session)) -> DatabaseProviderTypeItemSchema:
    """
    Retrieve a single instance of class DatabaseProviderType.

    :param database_provider_type_id: The ID of the instance to retrieve.
    :type database_provider_type_id: int
    :return: A JSON object containing the DatabaseProviderType instance data.
    :rtype: dict
    """

    database_provider_type = await DatabaseProviderTypeService(db).get(
        database_provider_type_id)
    if database_provider_type is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return database_provider_type

@router.get(
    "/database-provider-types/",
    tags=["DatabaseProviderType"],
    response_model=typing.List[DatabaseProviderTypeListSchema],
    response_model_exclude_none=True
)
async def find_database_provider_types(
    query_options: BaseQuerySchema = Depends(),
    db: AsyncSession = Depends(get_session)
) -> PaginatedSchema[DatabaseProviderTypeListSchema]:
    """
    Retrieve a list of instances using query options.
    :param query_options: Query options for sorting, filtering and paging.
    :return: A JSON object containing the list of instances data.
    :rtype: dict
    """
    return await DatabaseProviderTypeService(db).find(query_options)
