from typing import List, Optional
from sqlalchemy.engine import create_engine
import sqlalchemy as db
from sqlalchemy import ARRAY
from app.collector.sql_alchemy_collector import SqlAlchemyCollector
from app.collector import DEFAULT_UUID
from app.schemas import (
    DatabaseCreateSchema,
)
from app.collector.utils.constants_utils import SQLTYPES_DICT
from app.models import DataType

class HiveCollector(SqlAlchemyCollector):
    """Class to implement methods, to collect data in HIVE."""

    def _get_connection_string(self):
        params = self.connection_info
        if params is not None:
            return f"hive://{params.user_name}:{params.password}@{params.host}:{params.port}"
        return "FIXME"

    def get_connection_engine_for_tables(
        self, database_name: str, schema_name: str
    ):
        """Return the connection engine to get the tables."""
        engine = create_engine(self._get_connection_string()+f"/{schema_name}",
                               connect_args={'auth': 'LDAP'})
        return engine

    def get_view_names(self, schema_name: str,
                      engine, inspector) -> List[str]:
        """Return the views names."""

        view_names = []
        query = db.text("SHOW TABLES")
        with engine.connect() as conn:
            result = conn.execute(query)
            tables = result.fetchall()

            # Check the type of each table, e.g., using `DESCRIBE FORMATTED`
            for table in tables:
                table_name = table[0]
                describe_query = db.text(f"DESCRIBE FORMATTED {table_name}")

                desc_result = conn.execute(describe_query)
                describe = desc_result.fetchall()

                # Check if 'VIRTUAL_VIEW' is found in the table description (indicative of a view)
                if any("VIRTUAL_VIEW" in str(row) for row in describe):
                    view_names.append(table_name)
        return view_names

    def get_databases(self) -> List[DatabaseCreateSchema]:
        """Return all databases."""
        engine = create_engine(self._get_connection_string(), connect_args={'auth': 'LDAP'})
        insp = db.inspect(engine)
        result = insp.get_schema_names()
        engine.dispose()

        return [
            DatabaseCreateSchema(
                name=r,
                display_name=r,
                fully_qualified_name="placeholder",
                provider_id=DEFAULT_UUID,
            )
            for r in result
        ]

    def supports_schema(self):
        return False

    def get_connection_engine_for_schemas(
        self, database_name: str
    ) -> Optional[db.Engine]:
        """Return the connection engine to get the schemas."""
        return None

    def _get_ignorable_dbs(self) -> List[str]:
        return []

    def supports_pk(self) -> bool:
        """Return if the database supports primary keys."""
        return False

    def get_data_type_str(self, column) -> str:
        """Return the data type from a column."""
        data_type_str = SQLTYPES_DICT[str(column.get("type"))]
        return data_type_str
    
    
    def get_data_type_str(self, column) -> str:
        """Return the data type from a column."""
        column_type = column.get("type")
        
        data_type = SQLTYPES_DICT[
            str(column_type)
        ]
        data_type=DataType[data_type]
        
        array_data_type = None
        if isinstance(column_type, ARRAY):
            array_data_type = SQLTYPES_DICT[
                str(column.get("type").get("item_type"))
            ]
            array_data_type=DataType[array_data_type]
        
        return data_type, array_data_type
    
    

