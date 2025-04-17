from typing import List
from sqlalchemy.engine import create_engine

from app.collector.sql_alchemy_collector import SqlAlchemyCollector


class DruidCollector(SqlAlchemyCollector):
    """Class to implement methods to collect data in DRUID."""

    def _get_connection(self):
        params = self.connection_info
        if params is not None:
            return f"druid://{params.host}:{params.port}/druid/v2/sql/?header=true"
        return "FIXME"

    def get_connection_engine_for_tables(
        self, database_name: str, schema_name: str
    ):
        """Return the connection engine to get the tables."""
        connection = self._get_connection()
        engine = create_engine(connection, pool_pre_ping=True)
        return engine

    def get_databases(self) -> typing.List[DatabaseCreateSchema]:
        """Return all databases."""
        
        return [
            DatabaseCreateSchema(
                name="default",
                display_name="default",
                fully_qualified_name="placeholder",
                provider_id=DEFAULT_UUID,
            )
        ]

    def supports_schema(self):
        return False

    def supports_pk(self) -> bool:
        """Return if the database supports primary keys."""
        return False

    def supports_views(self) -> bool:
        """Return if the database supports views."""
        return False
