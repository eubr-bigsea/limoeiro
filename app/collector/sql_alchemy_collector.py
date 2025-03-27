import typing
from abc import abstractmethod
from typing import List

import sqlalchemy

from app.collector import DEFAULT_UUID
from app.collector.collector import Collector
from app.collector.utils.constants_utils import SQLTYPES_DICT
from app.models import DataType, TableType
from app.schemas import (
    DatabaseSchemaCreateSchema,
    DatabaseTableCreateSchema,
    TableColumnCreateSchema,
)


class SqlAlchemyCollector(Collector):
    """Class to implement methods, using SqlAlchemy, to collect data in collection engine."""

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_connection_engine_for_schemas(
        self, database_name: str
    ) -> typing.Optional[sqlalchemy.Engine]:
        """Return the connection engine to get the schemas."""
        pass

    @abstractmethod
    def get_connection_engine_for_tables(
        self, database_name: str, schema_name: str
    ) -> sqlalchemy.Engine:
        """Return the connection engine to get the tables."""
        pass

    # def get_database_names(self) -> List[str]:
    #     """Return all databases in a database provider using SqlAlchemy."""
    #     return self.get_schema_names("")

    def get_tables(
        self, database_name: str, schema_name: str
    ) -> List[DatabaseTableCreateSchema]:
        engine = self.get_connection_engine_for_tables(
            database_name, schema_name
        )
        inspector = sqlalchemy.inspect(engine)
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
                try:
                    unique_constraints = inspector.get_unique_constraints(
                        name, schema=schema_name
                    )
                except NotImplementedError:
                    print("FIXME, unique constraing not implemented")
                    unique_constraints = []

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
                            description=column.get(
                                "comment"
                            ),  # FIXME: add notes
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

                table_comment = inspector.get_table_comment(
                    name, schema=schema_name
                ).get("text")
                tables.append(
                    DatabaseTableCreateSchema(
                        name=name,
                        display_name=name,
                        fully_qualified_name=f"{database_name}.{schema_name}.{name}",
                        notes=table_comment,
                        database_id=DEFAULT_UUID,
                        columns=columns,
                        type=TableType[item_type],
                    )
                )
        engine.dispose()
        return tables

    @abstractmethod
    def _get_connection_string(self) -> str:
        return ""

    @abstractmethod
    def _get_ignorable_dbs(self) -> typing.List[str]:
        return []

    def _get_ignorable_schemas(self) -> typing.List[str]:
        return ["information_schema"]

    # FIXME: Review
    def _get_schema_fqn_elements(
        self, provider_name, database_name, schema_name
    ) -> List[str]:
        """Return the elements of the schema fqn."""
        return []

    def _get_table_fqn_elements(
        self, provider_name, database_name, schema_name, table_name
    ) -> List[str]:
        """Return the elements of the table fqn."""
        return []

    def _get_database_fqn_elements(
        self, provider_name, database_name
    ) -> List[str]:
        """Return the elements of the database fqn."""
        return []

    @abstractmethod
    def get_schemas(
        self, database_name: typing.Optional[str] = None
    ) -> List[DatabaseSchemaCreateSchema]:
        pass
