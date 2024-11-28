import os
from uuid import UUID
from typing import Union
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Path
from ..database import get_session
from ..models import Domain

router = APIRouter(prefix="/foo")
 
@router.get("/item/{item_id}", summary="Get an item from database")
async def get_item(item_id: Union[UUID, str] = Path(..., description="The ID of the item (UUID or string)"), 
    some=None, db: Session=Depends(get_session)):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    \f
    :param some: Identificador.
    """

    with db as session:
        if isinstance(item_id, str):
            d = session.query(Domain).filter(Domain.fully_qualified_name==item_id).first()
        else:
            d = session.query(Domain).filter(Domain.id==item_id).first()
        return d
