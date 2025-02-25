#
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status, Path

from ..schemas import (
    PaginatedSchema,
    DatabaseCreateSchema,
    DatabaseUpdateSchema,
    DatabaseItemSchema,
    DatabaseListSchema,
    DatabaseQuerySchema,
)
from ..services.database_service import DatabaseService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


@router.post(
    "/databases/",
    tags=["Database"],
    response_model=DatabaseItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_database(
    database_data: DatabaseCreateSchema, db: AsyncSession = Depends(get_session)
) -> DatabaseItemSchema:
    """
    Adiciona uma instância da classe Database.
    """

    database_data.updated_by = "FIXME!!!"

    return await DatabaseService(db).add(database_data)


@router.delete(
    "/databases/{database_id}",
    tags=["Database"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_databases(
    database_id: UUID, db: AsyncSession = Depends(get_session)
):
    """
    Exclui uma instância da classe Database.
    """
    await DatabaseService(db).delete(database_id)
    return


@router.patch(
    "/databases/{database_id}",
    tags=["Database"],
    response_model=DatabaseItemSchema,
    response_model_exclude_none=True,
)
async def update_databases(
    database_id: UUID = Path(..., description="Identificador"),
    database_data: DatabaseUpdateSchema = None,
    db: AsyncSession = Depends(get_session),
) -> DatabaseItemSchema:
    """
    Atualiza uma instância da classe Database.
    """

    database_data.updated_by = "FIXME!!!"

    return await DatabaseService(db).update(database_id, database_data)


@router.get(
    "/databases/",
    tags=["Database"],
    response_model=PaginatedSchema[DatabaseListSchema],
    response_model_exclude_none=True,
)
async def find_databases(
    query_options: DatabaseQuerySchema = Depends(),
    db: AsyncSession = Depends(get_session),
) -> PaginatedSchema[DatabaseListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    databases = await DatabaseService(db).find(query_options)
    model = DatabaseListSchema()
    databases.items = [model.model_validate(d) for d in databases.items]
    return databases


@router.get(
    "/databases/{database_id}",
    tags=["Database"],
    response_model=DatabaseItemSchema,
    response_model_exclude_none=False,
)
async def get_database(
    database_id: UUID = Path(..., description="Identificador"),
    db: AsyncSession = Depends(get_session),
) -> DatabaseItemSchema:
    """
    Recupera uma instância da classe Database.
    """

    database = await DatabaseService(db).get(database_id)
    if database is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return database
