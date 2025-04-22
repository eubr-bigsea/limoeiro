from typing import List, Optional
 
from sqlalchemy.engine import create_engine
import sqlalchemy

from app.collector.sql_alchemy_collector import SqlAlchemyCollector
from app.collector import DEFAULT_UUID
from app.schemas import (
    DatabaseCreateSchema,
    DatabaseSchemaCreateSchema,
    DatabaseTableCreateSchema
)


class DruidCollector(SqlAlchemyCollector):
    """Class to implement methods to collect data in DRUID."""

    def _get_connection_string(self):
        params = self.connection_info
        if params is not None:
            return f"druid://{params.host}:{params.port}/druid/v2/sql/?header=true"
        return "FIXME"

    def get_connection_engine_for_tables(
        self, database_name: str, schema_name: str
    ):
        """Return the connection engine to get the tables."""
        connection = self._get_connection_string()
        engine = create_engine(connection, pool_pre_ping=True)
        return engine

    def get_databases(self) -> List[DatabaseCreateSchema]:
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

    def get_connection_engine_for_schemas(
        self, database_name: str
    ) -> Optional[sqlalchemy.Engine]:
        """Return the connection engine to get the schemas."""
        return None

    def _get_ignorable_dbs(self) -> List[str]:
        return []

    def get_tables(
        self, database_name: str, schema_name: str
    ) -> List[DatabaseTableCreateSchema]:
        return super().get_tables(database_name, None)

