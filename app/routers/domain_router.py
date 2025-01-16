# 
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status, Path

from ..schemas import (
    PaginatedSchema,
    DomainCreateSchema,
    DomainUpdateSchema,
    DomainItemSchema,
    DomainListSchema,
    DomainQuerySchema,
)
from ..services.domain_service import DomainService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*

@router.post("/domains/",
    tags=["Domain"],
    response_model=DomainItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True)
async def add_domain(
    domain_data: DomainCreateSchema,
    db: AsyncSession = Depends(get_session)) -> DomainItemSchema:
    """
    Adiciona uma instância da classe Domain.
    """
    return await DomainService(db).add(
        domain_data)

@router.delete("/domains/{domain_id}",
    tags=["Domain"],
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_domains(domain_id: UUID,
    db: AsyncSession = Depends(get_session)) :
    """
    Exclui uma instância da classe Domain.
    """
    await DomainService(db).delete(domain_id)
    return

@router.patch("/domains/{domain_id}",
    tags=["Domain"],
    response_model=DomainItemSchema,
    response_model_exclude_none=True)
async def update_domains(domain_id: UUID=Path(..., description="Identificador"),
    domain_data: DomainUpdateSchema=None,
    db: AsyncSession = Depends(get_session)) -> DomainItemSchema:
    """
    Atualiza uma instância da classe Domain.
    """
    return await DomainService(db).update(
        domain_id, domain_data)

@router.get(
    "/domains/",
    tags=["Domain"],
    response_model=PaginatedSchema[DomainListSchema],
    response_model_exclude_none=True
)
async def find_domains(
    query_options: DomainQuerySchema = Depends(),
    db: AsyncSession = Depends(get_session)
) -> PaginatedSchema[DomainListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    domains = await DomainService(db).find(query_options)
    model = DomainListSchema()
    domains.items = [model.model_validate(d) for d in domains.items]
    return domains

@router.get("/domains/{domain_id}",
    tags=["Domain"],
    response_model=DomainItemSchema,
    response_model_exclude_none=False)
async def get_domain(domain_id: UUID = Path(..., description="Identificador"),
    db: AsyncSession = Depends(get_session)) -> DomainItemSchema:
    """
    Recupera uma instância da classe Domain.
    """

    domain = await DomainService(db).get(
        domain_id)
    if domain is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return domain
