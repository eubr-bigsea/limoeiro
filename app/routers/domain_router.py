#
import logging
import typing
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


def _get_service(db: AsyncSession = Depends(get_session)) -> DomainService:
    return DomainService(db)


@router.post(
    "/domains/",
    tags=["Domain"],
    response_model=DomainItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_domain(
    domain_data: DomainCreateSchema,
    service: DomainService = Depends(_get_service),
) -> DomainItemSchema:
    """
    Adiciona uma instância da classe Domain.
    """
    return await service.add(domain_data)


@router.delete(
    "/domains/{entity_id}",
    tags=["Domain"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_domains(
    domain_id: UUID = Path(..., description="Identificador"),
    service: DomainService = Depends(_get_service),
):
    """
    Exclui uma instância da classe Domain.
    """
    await service.delete(domain_id)
    return


@router.patch(
    "/domains/{entity_id}",
    tags=["Domain"],
    response_model=DomainItemSchema,
    response_model_exclude_none=True,
)
async def update_domains(
    domain_id: UUID = Path(..., description="Identificador"),
    domain_data: typing.Optional[DomainUpdateSchema] = None,
    service: DomainService = Depends(_get_service),
) -> DomainItemSchema:
    """
    Atualiza uma instância da classe Domain.
    """
    return await service.update(domain_id, domain_data)


@router.get(
    "/domains/",
    tags=["Domain"],
    response_model=PaginatedSchema[DomainListSchema],
    response_model_exclude_none=True,
)
async def find_domains(
    query_options: DomainQuerySchema = Depends(),
    service: DomainService = Depends(_get_service),
) -> PaginatedSchema[DomainListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    domains = await service.find(query_options)
    model = DomainListSchema()
    domains.items = [model.model_validate(d) for d in domains.items]
    return domains


@router.get(
    "/domains/{entity_id}",
    tags=["Domain"],
    response_model=DomainItemSchema,
    response_model_exclude_none=False,
)
async def get_domain(
    domain_id: UUID = Path(..., description="Identificador"),
    service: DomainService = Depends(_get_service),
) -> DomainItemSchema:
    """
    Recupera uma instância da classe Domain.
    """

    domain = await service.get(domain_id)
    if domain is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return domain
