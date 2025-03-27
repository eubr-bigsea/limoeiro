import typing
from typing import List

from sqlalchemy import text
from sqlalchemy.engine import create_engine

from app.collector import DEFAULT_UUID
from app.collector.sql_alchemy_collector import SqlAlchemyCollector
from app.schemas import (
    DatabaseCreateSchema,
    DatabaseProviderConnectionItemSchema,
    DatabaseSchemaCreateSchema,
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

    def get_schemas(
        self, database_name: typing.Optional[str] = None
    ) -> List[DatabaseSchemaCreateSchema]:
        return []

    def get_databases(self) -> typing.List[DatabaseCreateSchema]:
        """Return all databases."""
        engine = create_engine(self._get_connection_string())
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                        SELECT SCHEMA_NAME
                        FROM information_schema.SCHEMATA
                        WHERE SCHEMA_NAME NOT IN :ignore
                        """),
                {"ignore": tuple(self._get_ignorable_dbs())},
            ).fetchall()

        return [
            DatabaseCreateSchema(
                name=r[0],
                display_name=r[0],
                notes=None, # Not supported.
                fully_qualified_name="placeholder",
                provider_id=DEFAULT_UUID,
            )
            for r in result
        ]
