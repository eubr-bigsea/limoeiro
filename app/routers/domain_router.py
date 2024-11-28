import logging
import typing
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status

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
    Add a single instance of class Domain.

    :return: A JSON object containing a success message.
    :rtype: dict
    """
        
    domain_data.updated_by = "FIXME!!!"

    return await DomainService(db).add(
        domain_data)

@router.delete("/domains/{domain_id}",
    tags=["Domain"],
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_domains(domain_id: UUID,
    db: AsyncSession = Depends(get_session)) :
    """
    Delete a single instance of class Domain.

    :param domain_id: The ID of the instance to delete.
    :type domain_id: int
    :return: A JSON object containing a success message.
    :rtype: dict
    """
    await DomainService(db).delete(domain_id)
    return

@router.patch("/domains/{domain_id}",
    tags=["Domain"],
    response_model=DomainItemSchema,
    response_model_exclude_none=True)
async def update_domains(domain_id: UUID,
    domain_data: DomainUpdateSchema,
    db: AsyncSession = Depends(get_session)) -> DomainItemSchema:
    """
    Update a single instance of class Domain.

    :param domain_id: The ID of the instance to update.
    :type domain_id: int
    :return: A JSON object containing a success message.
    :rtype: dict
    """
        
    domain_data.updated_by = "FIXME!!!"

    return await DomainService(db).update(
        domain_id, domain_data)

@router.get(
    "/domains/",
    tags=["Domain"],
    response_model=typing.List[DomainListSchema],
    response_model_exclude_none=True
)
async def find_domains(
    query_options: DomainQuerySchema = Depends(),
    db: AsyncSession = Depends(get_session)
) -> PaginatedSchema[DomainListSchema]:
    """
    Retrieve a list of instances using query options.
    :param query_options: Query options for sorting, filtering and paging.
    :return: A JSON object containing the list of instances data.
    :rtype: dict
    """
    return await DomainService(db).find(query_options)

@router.get("/domains/{domain_id}",
    tags=["Domain"],
    response_model=DomainItemSchema,
    response_model_exclude_none=False)
async def get_domain(domain_id: UUID,
    db: AsyncSession = Depends(get_session)) -> DomainItemSchema:
    """
    Retrieve a single instance of class Domain.

    :param domain_id: The ID of the instance to retrieve.
    :type domain_id: int
    :return: A JSON object containing the Domain instance data.
    :rtype: dict
    """

    domain = await DomainService(db).get(
        domain_id)
    if domain is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return domain
