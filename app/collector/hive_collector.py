import typing
from sqlalchemy import Engine, text
from sqlalchemy.engine import create_engine

from app.collector import DEFAULT_UUID
from app.collector.sql_alchemy_collector import SqlAlchemyCollector
from app.schemas import DatabaseCreateSchema, DatabaseTableCreateSchema

IGNORE = []
IGNORE_SCHEMA = ["information_schema"]


class HiveCollector(SqlAlchemyCollector):
    """Class to implement methods, to collect data in HIVE."""

    def get_databases_names(self) -> typing.List[str]:
        """Return just the Default value."""
        database_list = ["default"]
        return database_list

    def _get_connection_string(self):
        params = self.connection_info
        if params is not None:
            if params.password and params.password != "" and False:  # FIXME
                return (
                    f"hive://{params.user_name}:{params.password}"
                    f"@{params.host}:{params.port}"
                )
            else:
                return f"hive://{params.host}:{params.port}"
        return "FIXME"

    def get_connection_engine_for_schemas(self, database_name: str):
        """Return the connection engine to get the schemas."""
        return create_engine(f"{self._get_connection_string()}/{database_name}")

    def get_connection_engine_for_tables(
        self, database_name: str, schema_name: str
    ):
        """Return the connection engine to get the tables."""
        return self.get_connection_engine_for_schemas(database_name)

    def supports_schema(self) -> bool:
        return False

    def _get_ignorable_dbs(self):
        return IGNORE

    def get_databases(self) -> typing.List[DatabaseCreateSchema]:
        """Return all databases."""
        engine = create_engine(self._get_connection_string())
        with engine.connect() as connection:
            result = [
                (r[0],)
                for r in connection.execute(text("SHOW DATABASES")).fetchall()
            ]
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

    def supports_pk(self):
        return False

    def supports_views(self):
        return False

    def post_process_table(
        self, engine: Engine, table: DatabaseTableCreateSchema
    ):
        with engine.connect() as connection:
            result = connection.execute(
                text(f"DESCRIBE FORMATTED {table.name}")
            ).fetchall()

            table_comment = None
            column_comments = {}

            for col, dt, comment in result:
                if dt is not None and dt.strip() == "comment":
                    table_comment = comment
                elif comment is not None and col is not None:
                    column_comments[col] = comment
            table.notes = table_comment
            if table.columns:
                for col in table.columns:
                    if col.name in column_comments:
                        col.description = column_comments[col.name]

        return table
