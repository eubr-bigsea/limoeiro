from abc import abstractmethod
from typing import List
import sqlalchemy as db

from app.collector.collector import (Collector, GenericTable, GenericColumn)


class SqlAlchemyCollector(Collector):
# Class to implement methods, using SqlAlchemy, to collect data in collection engine.
    
    def __init__(self, user: str, password: str, host: str, port: str):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
   
    @abstractmethod
    def get_connection_engine_for_schemas(self, database_name: str):
    # Return the connection engine to get the schemas.
        pass

    @abstractmethod
    def get_connection_engine_for_tables(self, database_name: str, schema_name: str):
    # Return the connection engine to get the tables.
        pass

    def get_schemas(self, database_name: str) -> List[str]:
    # Return all databases in a database provider using SqlAlchemy.
        engine = self.get_connection_engine_for_schemas(database_name)
        insp = db.inspect(engine)
        schema_list = insp.get_schema_names()
        engine.dispose()
        #return schema_list
        return ['trilhas']

    def get_tables(self, database_name: str, schema_name: str) -> List[GenericTable]:
    # Return all tables in a database provider using SqlAlchemy.
        engine = self.get_connection_engine_for_tables(database_name, schema_name)
        meta_data = db.MetaData()
        meta_data.reflect(bind=engine)       
        engine.dispose()
        
        generic_table_list = []
        table_list = meta_data.tables
        for table in table_list:
            
            generic_table = GenericTable(table)
            for column in table_list[table].columns:
                unique = column.unique if column.unique else False
                generic_table.add_column(GenericColumn(column.name, column.type, column.primary_key, column.nullable, unique))
            
            generic_table_list.append(generic_table)
        
        return generic_table_list
