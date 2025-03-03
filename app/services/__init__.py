import typing

from sqlalchemy import ScalarSelect, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base
from app.models import Tag
from app.schemas import BaseQuerySchema

T = typing.TypeVar('T', bound='Base')

class BaseService:
    def __init__(self, entity_type, session: AsyncSession):
        self.entity_type = entity_type
        self.session = session

    def get_by(self, field, value):
        ...
    def get_filters(
        self,
        cls: typing.Type[T],
        filter_opts: typing.Dict[str, tuple],
        query_options: BaseQuerySchema,
    ) -> typing.List:
        filters = []
        for param, (column, operator) in filter_opts.items():
            value = getattr(query_options, param, None)
            if value is not None:
                if operator == "tag":
                    tags = [tag.strip() for tag in value.split(',')]
                    filters.append(
                        cls.id.in_(self.get_tag_subquery(tags, cls.__name__)))
                else:
                    if operator == "ilike":
                        value = f"%{value}%"
                    if isinstance(column, (list, tuple)):
                        filters.append(
                            or_(*(getattr(c, operator)(value) for c in column))
                        )
                    else:
                        filters.append(getattr(column, operator)(value))
        return filters

    def get_tag_subquery(
        self, tags: typing.List[str], entity_type: str
    ) -> typing.Union[ScalarSelect[typing.Any], None] :
        if tags:
            # Subquery to find entity IDs with matching tags
            tag_subquery = (
                select(EntityTag.entity_id).where(
                    (EntityTag.entity_type == entity_type) & (Tag.name.in_(tags))
                )
            ).scalar_subquery()
            return tag_subquery
