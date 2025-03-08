#
import logging
import typing
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status, Path

from ..schemas import (
    PaginatedSchema,
    DatabaseTableCreateSchema,
    DatabaseTableUpdateSchema,
    DatabaseTableItemSchema,
    DatabaseTableListSchema,
    DatabaseTableQuerySchema,
)
from ..services.database_table_service import DatabaseTableService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(
    db: AsyncSession = Depends(get_session),
) -> DatabaseTableService:
    return DatabaseTableService(db)


@router.post(
    "/tables/",
    tags=["DatabaseTable"],
    response_model=DatabaseTableItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_database_table(
    database_table_data: DatabaseTableCreateSchema,
    service: DatabaseTableService = Depends(_get_service),
) -> DatabaseTableItemSchema:
    """
    Adiciona uma instância da classe DatabaseTable.
    """

    if database_table_data is not None:
        database_table_data.updated_by = "FIXME!!!"

    return await service.add(database_table_data)


@router.delete(
    "/tables/{database_table_id}",
    tags=["DatabaseTable"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_tables(
    database_table_id: UUID,
    service: DatabaseTableService = Depends(_get_service),
):
    """
    Exclui uma instância da classe DatabaseTable.
    """
    await service.delete(database_table_id)
    return


@router.patch(
    "/tables/{database_table_id}",
    tags=["DatabaseTable"],
    response_model=DatabaseTableItemSchema,
    response_model_exclude_none=True,
)
async def update_tables(
    database_table_id: UUID = Path(..., description="Identificador"),
    database_table_data: typing.Optional[DatabaseTableUpdateSchema] = None,
    service: DatabaseTableService = Depends(_get_service),
) -> DatabaseTableItemSchema:
    """
    Atualiza uma instância da classe DatabaseTable.
    """

    if database_table_data is not None:
        database_table_data.updated_by = "FIXME!!!"

    return await service.update(database_table_id, database_table_data)


@router.get(
    "/tables/",
    tags=["DatabaseTable"],
    response_model=PaginatedSchema[DatabaseTableListSchema],
    response_model_exclude_none=True,
)
async def find_tables(
    query_options: DatabaseTableQuerySchema = Depends(),
    service: DatabaseTableService = Depends(_get_service),
) -> PaginatedSchema[DatabaseTableListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    tables = await service.find(query_options)
    model = DatabaseTableListSchema()
    tables.items = [model.model_validate(d) for d in tables.items]
    return tables


@router.get(
    "/tables/{database_table_id}",
    tags=["DatabaseTable"],
    response_model=DatabaseTableItemSchema,
    response_model_exclude_none=False,
)
async def get_database_table(
    database_table_id: UUID = Path(..., description="Identificador"),
    service: DatabaseTableService = Depends(_get_service),
) -> DatabaseTableItemSchema:
    """
    Recupera uma instância da classe DatabaseTable.
    """

    database_table = await service.get(database_table_id)
    if database_table is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return database_table

@router.get(
    "/tables/fully_qualified_name/{fully_qualified_name}",
    tags=["DatabaseTable"],
    response_model=DatabaseTableItemSchema,
    response_model_exclude_none=False,
)
async def get_database_table_by_fully_qualified_name(
    fully_qualified_name: str = Path(..., description="Fully qualified name"),
    service: DatabaseTableService = Depends(_get_service),
) -> DatabaseTableItemSchema:
    """
    Recupera uma instância da classe DatabaseTable.
    """

    database_table = await service.get_by_fully_qualified_name(fully_qualified_name)
    if database_table is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return database_table
