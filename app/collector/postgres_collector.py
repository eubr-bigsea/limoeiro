from typing import List
import typing

from sqlalchemy import text
import sqlalchemy
from sqlalchemy.engine import create_engine

from app.collector.sql_alchemy_collector import SqlAlchemyCollector
from app.schemas import DatabaseProviderConnectionItemSchema

IGNORE = []
IGNORE_SCHEMA = ["information_schema"]


class PostgresCollector(SqlAlchemyCollector):
    """Class to implement methods, to collect data in HIVE."""

    connection_info: typing.Optional[DatabaseProviderConnectionItemSchema] = None

    def _get_connection_string(self):
        params = self.connection_info
        if params is not None:
            return (
                f"postgresql+psycopg2://{params.user_name}:{params.password}"
                f"@{params.host}:{params.port}"
            )
        return "FIXME"

    def _get_ignorable_dbs(self):
        return IGNORE

    def get_connection_engine_for_schemas(self, database_name: str):
        """Return the connection engine to get the schemas."""
        return create_engine(f"{self._get_connection_string()}/{database_name}")

    def get_connection_engine_for_tables(
        self, database_name: str, schema_name: str
    ):
        """Return the connection engine to get the tables."""
        return self.get_connection_engine_for_schemas(database_name)

    def get_databases_names(self) -> List[str]:
        """Return all databases."""
        engine = create_engine(self._get_connection_string())
        with engine.connect() as connection:
            result = [
                r[0]
                for r in connection.execute(
                    text("""
                    SELECT datname
                    FROM pg_database
                    WHERE datistemplate = false;
                    """)
                ).fetchall()
            ]
        return result

    def supports_schema(self):
        return True