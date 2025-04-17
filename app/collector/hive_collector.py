from typing import List
from sqlalchemy.engine import create_engine
import sqlalchemy as db

from app.collector.sql_alchemy_collector import SqlAlchemyCollector


class HiveCollector(SqlAlchemyCollector):
    """Class to implement methods, to collect data in HIVE."""

    def _get_connection(self):
        params = self.connection_info
        if params is not None:
            return f"hive://{params.user_name}:{params.password}@{params.host}:{params.port}"
        return "FIXME"

    def get_connection_engine_for_tables(
        self, database_name: str, schema_name: str
    ):
        """Return the connection engine to get the tables."""
        engine = create_engine(self._get_connection()+f"/{schema_name}", 
                               connect_args={'auth': 'LDAP'})
       
        return engine

    def get_view_names(self, schema_name: str,
                      engine, inspector) -> List[str]:
        """Return the views names."""
        
        view_names = []
        query = "SHOW TABLES"
        with engine.connect() as conn:
            result = conn.execute(query)
            tables = result.fetchall()

            # Now, you can check the type of each table, e.g., using `DESCRIBE FORMATTED`
            for table in tables:
                table_name = table[0]
                describe_query = f"DESCRIBE FORMATTED {table_name}"

                desc_result = conn.execute(describe_query)
                describe = desc_result.fetchall()

                # Check if 'VIRTUAL_VIEW' is found in the table description (indicative of a view)
                if any("VIRTUAL_VIEW" in str(row) for row in describe):
                    view_names.append(table_name)
        return view_names
    
    def get_databases(self) -> typing.List[DatabaseCreateSchema]:
        """Return all databases."""
        engine = create_engine(self._get_connection(), connect_args={'auth': 'LDAP'})
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

#    def get_tables(
#        self, database_name: str, schema_name: str
#    ) -> List[DatabaseTableCreateSchema]:
#        return super.get_tables(database_name, database_name)

    def supports_schema(self):
        return False

