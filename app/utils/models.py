from typing import List, Type, TypeVar, Union
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy.ext.declarative import DeclarativeMeta

from app.exceptions import EntityNotFoundException

T = TypeVar("T", bound=DeclarativeMeta)


async def update_model_instance(instance: T, update_data: BaseModel) -> None:
    """Generic method to update model instance attributes"""
    for field, value in update_data.dict(exclude_unset=True).items():
        if field != "id" and value is not None:
            setattr(instance, field, value)


async def update_collection(
    pk: Union[str, int, UUID],
    current_collection: List[T],
    updates: List[BaseModel],
    model_class: Type[T],
) -> List[T]:
    """
    Generic method to update a collection of related models (Items or Addresses)

    Args:
        pk: The ID of the parent order
        current_collection: Current list of model instances
        updates: List of update data
        model_class: The model class (Item or Address)
    """
    if not updates:
        return current_collection

    current_dict = {item.id: item for item in current_collection}
    updated_collection = []

    for update_data in updates:
        if update_data.id:
            # Update existing instance
            instance = current_dict.get(update_data.id)
            if not instance:
                raise EntityNotFoundException(
                    entity_type=str(model_class), entity_id=pk
                )
            await update_model_instance(instance, update_data)
            del current_dict[update_data.id]
            updated_collection.append(instance)
        else:
            # Create new instance
            new_data = update_data.model_dump(exclude_unset=True)
            new_instance = model_class(**new_data, order_id=pk)
            updated_collection.append(new_instance)

    # Keep remaining instances not included in the update
    updated_collection.extend(current_dict.values())
    return updated_collection
