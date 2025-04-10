import json
from typing import List
import typing

import oracledb
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


class OracleCollector(SqlAlchemyCollector):
    """Class to implement methods, to collect data in Oracle."""

    def _get_connection_string(self):
        params = self.connection_info
        if params is not None:
            if (
                params.extra_parameters is not None
                and params.extra_parameters != ""
            ):
                extra = json.loads(params.extra_parameters)
            else:
                extra = {"service_name": "xepdb1"}
            return (
                f"oracle+oracledb://{params.user_name}:{params.password}@"
                f"{params.host}:{params.port}/?service_name={extra.get('service_name')}"
            )
        return "FIXME"

    def _get_ignorable_dbs(self):
        return IGNORE

    def get_connection_engine_for_schemas(self, database_name: str):
        """Return the connection engine to get the schemas."""
        return create_engine(
            f"{self._get_connection_string()}",
            connect_args={
                "mode": oracledb.AUTH_MODE_SYSDBA,
            },
        )

    def get_connection_engine_for_tables(
        self, database_name: str, schema_name: str
    ):
        """Return the connection engine to get the tables."""
        return self.get_connection_engine_for_schemas(database_name)

    def get_databases(self) -> typing.List[DatabaseCreateSchema]:
        """Return all databases."""
        engine = create_engine(
            self._get_connection_string(),
            connect_args={
                "mode": oracledb.AUTH_MODE_SYSDBA,
            },
        )
        with engine.connect() as connection:
            result = [
                (r[0], r[1] if len(r) > 1 else None)
                for r in connection.execute(
                    text("SELECT name, '' FROM v$database")
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
        engine = create_engine(
            f"{self._get_connection_string()}",
            connect_args={
                "mode": oracledb.AUTH_MODE_SYSDBA,
            },
        )
        schemas = []
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                SELECT
                    username AS schema_name,
                    default_tablespace AS description
                FROM dba_users
                WHERE username NOT IN ('SYS', 'SYSTEM', 'OUTLN', 'DBSNMP',
                    'APPQOSSYS', 'AUDSYS', 'GSMADMIN_INTERNAL', 'ORDDATA',
                    'ORDPLUGINS', 'ORDDATA', 'ORDSYS', 'WMSYS', 'XDB', 'CTXSYS',
                    'MDSYS', 'LBACSYS', 'OLAPSYS', 'DVSYS', 'DVF',
                    'OJVMSYS', 'GGSYS', 'ANONYMOUS', 'APEX_PUBLIC_USER',
                    'FLOWS_FILES', 'APEX_%', 'PDBADMIN')
                    AND username NOT LIKE 'XDB'
                    AND common = 'NO'
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
