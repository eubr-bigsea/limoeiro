from typing import List
import typing

from sqlalchemy import text
from sqlalchemy.engine import create_engine

from app.collector import DEFAULT_UUID
from app.collector.sql_alchemy_collector import SqlAlchemyCollector
from app.schemas import (
    DatabaseCreateSchema,
    DatabaseSchemaCreateSchema,
)

IGNORE = []
IGNORE_SCHEMA = ["information_schema"]


class PostgresCollector(SqlAlchemyCollector):
    """Class to implement methods, to collect data in Postgres."""

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

    def get_databases(self) -> typing.List[DatabaseCreateSchema]:
        """Return all databases."""
        engine = create_engine(self._get_connection_string())
        with engine.connect() as connection:
            result = [
                (r[0], r[1])
                for r in connection.execute(
                    text("""
                SELECT d.datname, sh.description
                FROM pg_database d
                LEFT JOIN pg_shdescription sh ON d.oid = sh.objoid
                WHERE d.datistemplate = false;
                """)
                ).fetchall()
            ]

        return [
            DatabaseCreateSchema(
                name=r[0],
                display_name=r[0],
                notes=r[1],
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
            create_engine(f"{self._get_connection_string()}/{database_name}")
            if database_name
            else create_engine(self._get_connection_string())
        )
        schemas = []
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                SELECT
                    nspname,
                    obj_description(n.oid, 'pg_namespace') AS description
                FROM pg_namespace n
                WHERE nspname NOT IN ('information_schema', 'pg_catalog')
                    and nspname NOT LIKE 'pg_%';
                """)
            ).fetchall()
            for row in result:
                schema_name = row[0]
                schemas.append(
                    DatabaseSchemaCreateSchema(
                        name=schema_name,
                        display_name=schema_name,
                        fully_qualified_name="placeholder",
                        notes=row[1],
                        database_id=DEFAULT_UUID,
                    )
                )
        engine.dispose()
        return schemas
