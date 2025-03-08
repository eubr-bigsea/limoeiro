
from sqlalchemy.engine import create_engine
import sqlalchemy as db

from app.collector.sql_alchemy_collector import SqlAlchemyCollector

class DruidCollector(SqlAlchemyCollector):
# Class to implement methods to collect data in DRUID.

    def get_databases(self):
    # Return just the Default value.

        database_list = ['default']
        return database_list

    def get_schemas(self, database_name):
    # Return just the Default value.

        database_list = ['default']
        return database_list

    def get_connection_engine_for_schemas(self, database_name):
    # Return the connection engine to get the schemas.
        connection = f'druid://{self.host}:{self.port}/druid/v2/sql/?header=true'
        engine = create_engine(connection, pool_pre_ping=True)
        return engine

    def get_connection_engine_for_tables(self, database_name, schema_name):
    # Return the connection engine to get the tables.
        connection = f'druid://{self.host}:{self.port}/druid/v2/sql/?header=true'
        engine = create_engine(connection, pool_pre_ping=True)
        return engine
