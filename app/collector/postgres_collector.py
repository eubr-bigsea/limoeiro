from typing import List
from sqlalchemy.engine import create_engine
import sqlalchemy as db

from app.collector.sql_alchemy_collector import SqlAlchemyCollector

class PostgresCollector(SqlAlchemyCollector):
# Class to implement methods, to collect data in HIVE.

    def get_databases(self) -> List[str]:
    # Return all databases.
        engine = create_engine(f'postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}')
        result = engine.execute('SELECT datname FROM pg_database;').fetchall()
        result = [r[0] for r in result]
        result

    def get_connection_engine_for_schemas(self, database_name: str):
    # Return the connection engine to get the schemas.
        connection = f'postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{database_name}'
        engine = create_engine(connection)
        return engine

    def get_connection_engine_for_tables(self, database_name: str, schema_name: str):
    # Return the connection engine to get the tables.
        connection = f'postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{database_name}'
        engine = create_engine(connection, connect_args={'options': '-csearch_path={}'.format(schema_name)})
        return engine
