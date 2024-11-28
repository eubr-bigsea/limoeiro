from sqlalchemy import or_
import typing

from app.schemas import BaseQuerySchema


class BaseService:
    def __init__(self, entity_type):
        self.entity_type = entity_type

    def get_filters(
        self,
        filter_opts: typing.Dict[str, tuple],
        query_options: BaseQuerySchema,
    ) -> typing.List:
        filters = []
        for param, (column, operator) in filter_opts.items():
            value = getattr(query_options, param, None)
            if value is not None:
                if operator == "ilike":
                    value = f"%{value}%"
                if isinstance(column, (list, tuple)):
                    filters.append(
                        or_(*(getattr(c, operator)(value) for c in column))
                    )
                else:
                    filters.append(getattr(column, operator)(value))
        return filters
