#
import logging
import typing
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status, Path

from ..schemas import (
    PaginatedSchema,
    CompanyCreateSchema,
    CompanyUpdateSchema,
    CompanyItemSchema,
    CompanyListSchema,
    CompanyQuerySchema,
)
from ..services.company_service import CompanyService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(db: AsyncSession = Depends(get_session)) -> CompanyService:
    return CompanyService(db)


@router.post(
    "/companies/",
    tags=["Company"],
    response_model=CompanyItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_company(
    company_data: CompanyCreateSchema,
    service: CompanyService = Depends(_get_service),
) -> CompanyItemSchema:
    """
    Adiciona uma instância da classe Company.
    """
    return await service.add(company_data)


@router.delete(
    "/companies/{company_id}",
    tags=["Company"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_companies(
    company_id: UUID = Path(..., description="Identificador"),
    service: CompanyService = Depends(_get_service),
):
    """
    Exclui uma instância da classe Company.
    """
    await service.delete(company_id)
    return


@router.patch(
    "/companies/{company_id}",
    tags=["Company"],
    response_model=CompanyItemSchema,
    response_model_exclude_none=True,
)
async def update_companies(
    company_id: UUID = Path(..., description="Identificador"),
    company_data: typing.Optional[CompanyUpdateSchema] = None,
    service: CompanyService = Depends(_get_service),
) -> CompanyItemSchema:
    """
    Atualiza uma instância da classe Company.
    """
    return await service.update(company_id, company_data)


@router.get(
    "/companies/",
    tags=["Company"],
    response_model=PaginatedSchema[CompanyListSchema],
    response_model_exclude_none=True,
)
async def find_companies(
    query_options: CompanyQuerySchema = Depends(),
    service: CompanyService = Depends(_get_service),
) -> PaginatedSchema[CompanyListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    companies = await service.find(query_options)
    model = CompanyListSchema()
    companies.items = [model.model_validate(d) for d in companies.items]
    return companies


@router.get(
    "/companies/{company_id}",
    tags=["Company"],
    response_model=CompanyItemSchema,
    response_model_exclude_none=False,
)
async def get_company(
    company_id: UUID = Path(..., description="Identificador"),
    service: CompanyService = Depends(_get_service),
) -> CompanyItemSchema:
    """
    Recupera uma instância da classe Company.
    """

    company = await service.get(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return company
