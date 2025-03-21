#
import logging
import typing
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status, Path

from ..schemas import (
    PaginatedSchema,
    ContactCreateSchema,
    ContactUpdateSchema,
    ContactItemSchema,
    ContactListSchema,
    ContactQuerySchema,
)
from ..services.contact_service import ContactService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(db: AsyncSession = Depends(get_session)) -> ContactService:
    return ContactService(db)


@router.post(
    "/contacts/",
    tags=["Contact"],
    response_model=ContactItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_contact(
    contact_data: ContactCreateSchema,
    service: ContactService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
) -> ContactItemSchema:
    """
    Adiciona uma instância da classe Contact.
    """
    result = await service.add(contact_data)
    await session.commit()
    return result


@router.delete(
    "/contacts/{contact_id}",
    tags=["Contact"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_contacts(
    contact_id: UUID = Path(..., description="Identificador"),
    service: ContactService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
):
    """
    Exclui uma instância da classe Contact.
    """
    await service.delete(contact_id)
    await session.commit()
    return


@router.patch(
    "/contacts/{contact_id}",
    tags=["Contact"],
    response_model=ContactItemSchema,
    response_model_exclude_none=True,
)
async def update_contacts(
    contact_id: UUID = Path(..., description="Identificador"),
    contact_data: typing.Optional[ContactUpdateSchema] = None,
    service: ContactService = Depends(_get_service),
    session: AsyncSession = Depends(get_session),
) -> ContactItemSchema:
    """
    Atualiza uma instância da classe Contact.
    """
    result = await service.update(contact_id, contact_data)
    await session.commit()
    return result


@router.get(
    "/contacts/",
    tags=["Contact"],
    response_model=PaginatedSchema[ContactListSchema],
    response_model_exclude_none=True,
)
async def find_contacts(
    query_options: ContactQuerySchema = Depends(),
    service: ContactService = Depends(_get_service),
) -> PaginatedSchema[ContactListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    contacts = await service.find(query_options)
    model = ContactListSchema()
    contacts.items = [model.model_validate(d) for d in contacts.items]
    return contacts


@router.get(
    "/contacts/{contact_id}",
    tags=["Contact"],
    response_model=ContactItemSchema,
    response_model_exclude_none=False,
)
async def get_contact(
    contact_id: UUID = Path(..., description="Identificador"),
    service: ContactService = Depends(_get_service),
) -> ContactItemSchema:
    """
    Recupera uma instância da classe Contact.
    """

    contact = await service.get(contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return contact
