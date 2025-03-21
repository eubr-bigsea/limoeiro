#
import logging
import typing
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends, status, Path

from ..schemas import (
    PaginatedSchema,
    PersonCreateSchema,
    PersonUpdateSchema,
    PersonItemSchema,
    PersonListSchema,
    PersonQuerySchema,
)
from ..services.person_service import PersonService
from ..database import get_session

router = APIRouter()
log = logging.getLogger(__name__)
# region Protected\s*
# endregion\w*


def _get_service(db: AsyncSession = Depends(get_session)) -> PersonService:
    return PersonService(db)


@router.post(
    "/people/",
    tags=["Person"],
    response_model=PersonItemSchema,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def add_person(
    person_data: PersonCreateSchema,
    service: PersonService = Depends(_get_service),
) -> PersonItemSchema:
    """
    Adiciona uma instância da classe Person.
    """
    return await service.add(person_data)


@router.delete(
    "/people/{person_id}",
    tags=["Person"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_people(
    person_id: UUID = Path(..., description="Identificador"),
    service: PersonService = Depends(_get_service),
):
    """
    Exclui uma instância da classe Person.
    """
    await service.delete(person_id)
    return


@router.patch(
    "/people/{person_id}",
    tags=["Person"],
    response_model=PersonItemSchema,
    response_model_exclude_none=True,
)
async def update_people(
    person_id: UUID = Path(..., description="Identificador"),
    person_data: typing.Optional[PersonUpdateSchema] = None,
    service: PersonService = Depends(_get_service),
) -> PersonItemSchema:
    """
    Atualiza uma instância da classe Person.
    """
    return await service.update(person_id, person_data)


@router.get(
    "/people/",
    tags=["Person"],
    response_model=PaginatedSchema[PersonListSchema],
    response_model_exclude_none=True,
)
async def find_people(
    query_options: PersonQuerySchema = Depends(),
    service: PersonService = Depends(_get_service),
) -> PaginatedSchema[PersonListSchema]:
    """
    Recupera uma lista de instâncias usando as opções de consulta.
    """
    people = await service.find(query_options)
    model = PersonListSchema()
    people.items = [model.model_validate(d) for d in people.items]
    return people


@router.get(
    "/people/{person_id}",
    tags=["Person"],
    response_model=PersonItemSchema,
    response_model_exclude_none=False,
)
async def get_person(
    person_id: UUID = Path(..., description="Identificador"),
    service: PersonService = Depends(_get_service),
) -> PersonItemSchema:
    """
    Recupera uma instância da classe Person.
    """

    person = await service.get(person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return person
