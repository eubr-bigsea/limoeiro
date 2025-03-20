#
import logging
import typing
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status, Path

from ..schemas import (
    PaginatedSchema,
    DatabaseTableSampleCreateSchema,
    DatabaseTableSampleUpdateSchema,
    DatabaseTableSampleItemSchema,
    DatabaseTableSampleListSchema,
)
from ..services.database_table_sample_service import DatabaseTableSampleService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(
    db: AsyncSession = Depends(get_session),
) -> DatabaseTableSampleService:
    return DatabaseTableSampleService(db)


@router.post(
    "/samples/",
    tags=["DatabaseTableSample"],
    response_model=DatabaseTableSampleItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_database_table_sample(
    database_table_sample_data: DatabaseTableSampleCreateSchema,
    service: DatabaseTableSampleService = Depends(_get_service),
) -> DatabaseTableSampleItemSchema:
    """
    Adiciona uma instância da classe DatabaseTableSample.
    """

    if database_table_sample_data is not None:
        database_table_sample_data.updated_by = "FIXME!!!"

    return await service.add(database_table_sample_data)


@router.delete(
    "/samples/{database_table_sample_id}",
    tags=["DatabaseTableSample"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_samples(
    database_table_sample_id: UUID = Path(..., description="Identificador"),
    service: DatabaseTableSampleService = Depends(_get_service),
):
    """
    Exclui uma instância da classe DatabaseTableSample.
    """
    await service.delete(database_table_sample_id)
    return


@router.patch(
    "/samples/{database_table_sample_id}",
    tags=["DatabaseTableSample"],
    response_model=DatabaseTableSampleItemSchema,
    response_model_exclude_none=True,
)
async def update_samples(
    database_table_sample_id: UUID = Path(..., description="Identificador"),
    database_table_sample_data: typing.Optional[
        DatabaseTableSampleUpdateSchema
    ] = None,
    service: DatabaseTableSampleService = Depends(_get_service),
) -> DatabaseTableSampleItemSchema:
    """
    Atualiza uma instância da classe DatabaseTableSample.
    """

    if database_table_sample_data is not None:
        database_table_sample_data.updated_by = "FIXME!!!"

    return await service.update(
        database_table_sample_id, database_table_sample_data
    )


@router.get(
    "/samples/",
    tags=["DatabaseTableSample"],
    response_model=PaginatedSchema[DatabaseTableSampleListSchema],
    response_model_exclude_none=True,
)
async def find_samples(
    query_options: DatabaseTableSampleQuerySchema = Depends(),
    service: DatabaseTableSampleService = Depends(_get_service),
) -> PaginatedSchema[DatabaseTableSampleListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    samples = await service.find(query_options)
    model = DatabaseTableSampleListSchema()
    samples.items = [model.model_validate(d) for d in samples.items]
    return samples


@router.get(
    "/samples/{database_table_sample_id}",
    tags=["DatabaseTableSample"],
    response_model=DatabaseTableSampleItemSchema,
    response_model_exclude_none=False,
)
async def get_database_table_sample(
    database_table_sample_id: UUID = Path(..., description="Identificador"),
    service: DatabaseTableSampleService = Depends(_get_service),
) -> DatabaseTableSampleItemSchema:
    """
    Recupera uma instância da classe DatabaseTableSample.
    """

    database_table_sample = await service.get(database_table_sample_id)
    if database_table_sample is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return database_table_sample
