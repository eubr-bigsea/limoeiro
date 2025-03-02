import typing

from pydantic import BaseModel

from ..database import Base

# async def update_model_instance(instance: T, update_data: BaseModel) -> None:
#     """Generic method to update model instance attributes"""
#     for field, value in update_data.dict(exclude_unset=True).items():
#         if field != "id" and value is not None:
#             setattr(instance, field, value)


def update_related_collection(
    collection: typing.List[typing.Any],
    updates: typing.Sequence[BaseModel],
    model_class: typing.Type[Base],
    parent_id_field: str,
    parent_id_value: typing.Any,
) -> typing.List[BaseModel]:
    """
    Generic function to update a collection of related objects.

    Args:
        collection: The collection in the parent object
        updates: List of Pydantic models containing the updates
        model_class: The SQLAlchemy model class for creating new instances
        parent_id_field: The field name that links to the parent in the model
        parent_id_value: The value of the parent ID
        delete_missing: Whether to delete items not included in updates
    """

    # Create a mapping of existing items by ID
    item_map = {str(item.id): item for item in collection}  # type: ignore

    # Keep track of processed IDs
    processed_ids = set()

    # Process updates
    ok_updates = filter(
        lambda u: u,
        map(
            lambda u: u.model_dump(exclude_unset=True, exclude_none=True),
            updates,
        ),
    )
    for item_update in ok_updates:
        item_data = item_update
        item_id = item_data.pop("id", None)

        if item_id and str(item_id) in item_map:
            # Update existing item
            for field, value in item_data.items():
                setattr(item_map[str(item_id)], field, value)
            processed_ids.add(str(item_id))
        else:
            # Create new item
            item_data[parent_id_field] = parent_id_value
            new_item = model_class(**item_data)
            collection.append(new_item)

    # Optionally remove items not in the update
    return [
        item
        for item in collection
        if item.id and str(item.id) not in processed_ids
    ]
