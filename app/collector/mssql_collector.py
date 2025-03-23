from typing import List
import typing

from sqlalchemy import text
from sqlalchemy.engine import create_engine

from app.collector import DEFAULT_UUID
from app.collector.sql_alchemy_collector import SqlAlchemyCollector
from app.schemas import (
    DatabaseCreateSchema,
    DatabaseProviderConnectionItemSchema,
    DatabaseSchemaCreateSchema,
)

IGNORE =  ['master', 'tempdb', 'model', 'msdb']
IGNORE_SCHEMA = ["information_schema"]


class SqlServerCollector(SqlAlchemyCollector):
    """Class to implement methods, to collect data in SQL Server."""

    connection_info: typing.Optional[DatabaseProviderConnectionItemSchema] = None

    def _get_connection_string(self):
        params = self.connection_info
        if params is not None:
            return (
                f"mssql+pymssql://{params.user_name}:{params.password}"
                f"@{params.host}:{params.port}"
            )
        return "FIXME"

    def _get_ignorable_dbs(self):
        return IGNORE

    def get_connection_engine_for_schemas(self, database_name: str):
        """Return the connection engine to get the schemas."""
        return create_engine(
            f"{self._get_connection_string()}/{database_name}",
            connect_args={"timeout": 10},
        )

    def get_connection_engine_for_tables(
        self, database_name: str, schema_name: str
    ):
        """Return the connection engine to get the tables."""
        return self.get_connection_engine_for_schemas(database_name)

    def get_databases(self) -> typing.List[DatabaseCreateSchema]:
        """Return all databases."""
        engine = create_engine(
            self._get_connection_string(), connect_args={"timeout": 10}
        )
        ignorable = ', '.join([f"'{d}'" for d in IGNORE])
        with engine.connect() as connection:
            result = connection.execute(
                text(f"""
                SELECT d.name
                FROM sys.databases d
                WHERE d.name NOT IN ({ignorable});
                """)
            ).fetchall()

        return [
            DatabaseCreateSchema(
                name=r[0],
                display_name=r[0],
                notes=None,  # Not supported
                fully_qualified_name="placeholder",
                provider_id=DEFAULT_UUID,
            )
            for r in result
        ]

    def supports_schema(self):
        return True

    def get_schemas(
        self, database_name: typing.Optional[str] = None
    ) -> List[DatabaseSchemaCreateSchema]:
        engine = (
            create_engine(
                f"{self._get_connection_string()}/{database_name}",
                connect_args={"timeout": 10},
            )
            if database_name
            else create_engine(
                self._get_connection_string(),
                connect_args={"timeout": 10},
            )
        )
        schemas = []
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                SELECT
                    s.name AS schema_name
                FROM sys.schemas s
                WHERE s.name NOT IN ('information_schema', 'sys')
                AND s.name NOT LIKE 'db[_]%';
                """)
            ).fetchall()
            for row in result:
                schema_name = row[0]
                schemas.append(
                    DatabaseSchemaCreateSchema(
                        name=schema_name,
                        display_name=schema_name,
                        fully_qualified_name="placeholder",
                        notes=None, #Not supported
                        database_id=DEFAULT_UUID,
                    )
                )
        engine.dispose()
        return schemas
