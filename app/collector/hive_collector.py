
from sqlalchemy.engine import create_engine
import sqlalchemy as db

from app.collector.sql_alchemy_collector import SqlAlchemyCollector

class HiveCollector(SqlAlchemyCollector):
# Class to implement methods, to collect data in HIVE.

    def get_databases(self) -> List[str]:
    # Return just the Default value.
        database_list = ['default']
        return database_list

    def get_connection_engine_for_schemas(self, database_name):
    # Return the connection engine to get the schemas.
        connection = f"hive://{self.user}:{self.password}@{self.host}:{self.port}"
        engine = create_engine(connection, connect_args={'auth': 'LDAP'})
        return engine

    def get_connection_engine_for_tables(self, database_name, schema_name):
    # Return the connection engine to get the tables.
        connection =  f"hive://{self.user}:{self.password}@{self.host}:{self.port}/{schema_name}"
        engine = create_engine(connection, connect_args={'auth': 'LDAP'})
        return engine
