import typing
from typing import List

import sqlalchemy
from sqlalchemy import inspect
from sqlalchemy.engine import create_engine

from app.collector import DEFAULT_UUID
from app.collector.collector import GenericTable
from app.collector.sql_alchemy_collector import SqlAlchemyCollector
from app.collector.utils.constants_utils import SQLTYPES_DICT
from app.models import DataType, TableType
from app.schemas import (
    DatabaseProviderConnectionItemSchema,
    DatabaseTableCreateSchema,
    TableColumnCreateSchema,
)

IGNORE = ["information_schema", "performance_schema", "mysql", "sys"]


class MariaDbCollector(SqlAlchemyCollector):
    """Class to implement methods, to collect data in HIVE."""

    # __slots__ = ['ingestion', 'connection_info']
    connection_info: typing.Optional[DatabaseProviderConnectionItemSchema] = None

    def _get_connection_string(self):
        params = self.connection_info
        if params is not None:
            return (
                f"mysql+pymysql://{params.user_name}:{params.password}"
                f"@{params.host}:{params.port}"
            )
        return "FIXME"

    def _get_ignorable_dbs(self):
        return IGNORE

    def get_connection_engine_for_schemas(self, database_name: str):
        """Return the connection engine to get the schemas."""
        return create_engine(self._get_connection_string())

    def get_connection_engine_for_tables(
        self, database_name: str, schema_name: str
    ):
        """Return the connection engine to get the tables."""
        return self.get_connection_engine_for_schemas(database_name)

    def get_databases_names(self) -> List[str]:
        """Return databases."""
        return self.get_schema_names()

    def get_tables(
        self, database_name: str, schema_name: str
    ) -> List[DatabaseTableCreateSchema]:
        engine = self.get_connection_engine_for_tables(
            database_name, schema_name
        )
        inspector = inspect(engine)
        tables = []
        view_names = inspector.get_view_names(schema=schema_name)
        table_names = inspector.get_table_names(schema=schema_name)
        for item_type, items in zip(
            ["VIEW", "REGULAR"], [view_names, table_names]
        ):
            for name in items:
                table_info = inspector.get_table_comment(
                    name, schema=schema_name
                )
                columns: typing.List[TableColumnCreateSchema] = []
                primary_keys = inspector.get_pk_constraint(
                    name, schema=schema_name
                ).get("constrained_columns", [])
                unique_constraints = inspector.get_unique_constraints(
                    name, schema=schema_name
                )
                unique_columns = [
                    col
                    for constraint in unique_constraints
                    for col in constraint.get("column_names", [])
                    if len(constraint.get("column_names", [])) == 1
                ]

                for i, column in enumerate(
                    inspector.get_columns(name, schema=schema_name)
                ):
                    data_type_str = SQLTYPES_DICT[
                        column.get("type").__class__.__name__.upper()
                    ]
                    columns.append(
                        TableColumnCreateSchema(
                            name=column.get("name"),
                            description=column.get("comment"),
                            display_name=column.get("name"),
                            data_type=DataType[data_type_str],
                            size=getattr(column.get("type"), "length", None),
                            precision=getattr(
                                column.get("type"), "precision", None
                            ),
                            scale=getattr(column.get("type"), "scale", None),
                            nullable=column.get("nullable"),
                            position=i,
                            primary_key=column.get("name") in primary_keys,
                            unique=column.get("name") in unique_columns,
                            # is_metadata=False,
                            # array_data_type=None,
                            # semantic_type=None
                            default_value=column.get("default"),
                        )
                    )
                tables.append(
                    DatabaseTableCreateSchema(
                        name=name,
                        display_name=name,
                        fully_qualified_name=f"{database_name}.{name}",
                        description=table_info.get("text"),
                        database_id=DEFAULT_UUID,
                        columns=columns,
                        type=TableType[item_type],
                    )
                )
        engine.dispose()
        return tables
