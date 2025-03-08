from abc import abstractmethod
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
    def get_connection_engine_for_schemas(self, database_name):
    # Return the connection engine to get the schemas.
        pass

    @abstractmethod
    def get_connection_engine_for_tables(self, database_name, schema_name):
    # Return the connection engine to get the tables.
        pass

    def get_schemas(self, database_name) -> List[str]:
    # Return all databases in a database provider using SqlAlchemy.
        engine = self.get_connection_engine_for_schemas(database_name)
        insp = db.inspect(engine)
        schema_list = insp.get_schema_names()
        engine.dispose()
        #return schema_list
        return ['trilhas']

    def get_tables(self, database_name, schema_name) -> List[GenericTable]:
    # Return all tables in a database provider using SqlAlchemy.
        engine = self.get_connection_engine_for_tables(database_name, schema_name)
        meta_data = db.MetaData()
        meta_data.reflect(bind=engine)       
        engine.dispose()
        
        generic_table_list = []
        table_list = meta_data.tables
        for table in table_list:
            
            generic_table = GenericTable(table)
            for column_obj in table_list[table].columns:
                generic_table.add_column(GenericColumn(column_obj.name, column_obj.type))
            
            generic_table_list.append(generic_table)
        
        return generic_table_list
