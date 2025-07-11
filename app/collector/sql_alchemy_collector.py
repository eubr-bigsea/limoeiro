import logging
import typing
from abc import abstractmethod
from typing import List

import sqlalchemy
from sqlalchemy import ARRAY
from app.collector import DEFAULT_UUID
from app.collector.collector import Collector
from app.collector.utils.constants_utils import SQLTYPES_DICT
from app.models import DataType, TableType
from app.schemas import (
    DatabaseSchemaCreateSchema,
    DatabaseTableCreateSchema,
    TableColumnCreateSchema,
    DatabaseTableSampleCreateSchema,
)
from datetime import datetime
logger = logging.getLogger(__name__)


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

    def supports_pk(self) -> bool:
        """Return if the database supports primary keys."""
        return True

    def supports_views(self) -> bool:
        """Return if the database supports views."""
        return True

    def get_view_names(self, schema_name: str,
                      engine, inspector) -> List[str]:
        """Return the views names."""
        return inspector.get_view_names(schema=schema_name)

    def post_process_table(
        self, engine: sqlalchemy.Engine, table: DatabaseTableCreateSchema
    ):
        """Post process the table."""
        return table

    @abstractmethod
    def get_connection_engine_for_tables(
        self, database_name: str, schema_name: str
    ) -> sqlalchemy.Engine:
        """Return the connection engine to get the tables."""
        pass

    def get_data_type_str(self, column) -> str:
        """Return the data type from a column."""
        column_type = column.get("type")
        
        data_type = SQLTYPES_DICT[
            column_type.__class__.__name__.upper()
        ]
        data_type=DataType[data_type]
                            
        
        array_data_type = None
        if isinstance(column_type, ARRAY):
            array_data_type = SQLTYPES_DICT[
                column.get("type").get("item_type").__class__.__name__.upper()
            ]
            array_data_type=DataType[array_data_type]
        
        return data_type, array_data_type


    def get_table_comment (self, name, schema_name, inspector, engine):
        try:
            table_comment = inspector.get_table_comment(
                name, schema=schema_name
            ).get("text")
        except NotImplementedError:
            table_comment = None

        return table_comment

    def get_column_comment (self, column, name):
        return column.get("comment")

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
        if self.supports_views():
            view_names = self.get_view_names(schema_name, engine, inspector)
        else:
            view_names = []
            logger.info("Provedor de dados não suporta views")
        table_names = inspector.get_table_names(schema=schema_name)
        for item_type, items in zip(
            ["VIEW", "REGULAR"], [view_names, table_names]
        ):
            for name in items:
                
                
                columns: typing.List[TableColumnCreateSchema] = []
                if self.supports_pk():
                    primary_keys = inspector.get_pk_constraint(
                        name, schema=schema_name
                    ).get("constrained_columns", [])
                else:
                    primary_keys = []
                try:
                    unique_constraints = inspector.get_unique_constraints(
                        name, schema=schema_name
                    )
                except NotImplementedError:
                    logger.info(
                        "Provedor de dados não suporta unique constraint"
                    )
                    unique_constraints = []

                unique_columns = [
                    col
                    for constraint in unique_constraints
                    for col in constraint.get("column_names", [])
                    if len(constraint.get("column_names", [])) == 1
                ]

                # Get the table comment
                table_comment = self.get_table_comment(name, schema_name ,inspector, engine)

                for i, column in enumerate(
                    inspector.get_columns(name, schema=schema_name)
                ):
                    data_type, array_data_type = self.get_data_type_str(column)

                    # Get the column comment
                    column_comment = self.get_column_comment(column, column.get("name"))

                    columns.append(
                        TableColumnCreateSchema(
                            name=column.get("name"),
                            description=column_comment,
                            display_name=column.get("name"),
                            data_type=data_type,
                            array_data_type=array_data_type,
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
                    
                    

                if self.supports_schema():
                    table_fqn = f"{database_name}.{schema_name}.{name}"
                else:
                    table_fqn = f"{database_name}.{name}"

                database_table = self.post_process_table(
                    engine,
                    DatabaseTableCreateSchema(
                        name=name,
                        display_name=name,
                        fully_qualified_name=table_fqn,
                        notes=table_comment,
                        database_id=DEFAULT_UUID,
                        columns=columns,
                        type=TableType[item_type],
                    ),
                )
                tables.append(database_table)
        engine.dispose()

        return tables

    def get_samples(self, database_name: str,
                    schema_name: str, table: DatabaseTableCreateSchema
    ) -> DatabaseTableSampleCreateSchema:
        """Return the samples from a column."""

        metadata = sqlalchemy.MetaData()
        engine = self.get_connection_engine_for_tables(
                     database_name, schema_name
                 )
        
        # Reflect the table from the database
        with engine.connect() as conn:
            metadata.reflect(bind=conn, only=[table.name])
            table = metadata.tables[table.name]

            # Generic SELECT with LIMIT
            stmt = sqlalchemy.select(table).limit(10)
            result = conn.execute(stmt)
            rows = result.mappings().all()
            rows = [dict(row) for row in rows]

        engine.dispose()
        return DatabaseTableSampleCreateSchema(
                                date=datetime.now(),
                                content=rows,
                                is_visible=True,
                                database_table_id=DEFAULT_UUID,
        )

    @abstractmethod
    def _get_connection_string(self) -> str:
        return ""

    @abstractmethod
    def _get_ignorable_dbs(self) -> typing.List[str]:
        return []

    def _get_ignorable_schemas(self) -> typing.List[str]:
        return ["information_schema"]

    def get_schemas(
        self, database_name: typing.Optional[str] = None
    ) -> List[DatabaseSchemaCreateSchema]:
        return []
