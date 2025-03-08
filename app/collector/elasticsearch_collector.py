from abc import abstractmethod
import sqlalchemy as db

from app.collector.collector import (Collector, GenericTable, GenericColumn)
from elasticsearch import Elasticsearch

class ElasticsearchCollector(Collector):
# Class to implement methods, using SqlAlchemy, to collect data in collection engine.
    
    def __init__(self, user: str, password: str, host: str, port: str):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
   
    def get_databases(self) -> List[str]:
    # Return just the Default value.

        database_list = ['default']
        return database_list

    def get_schemas(self, database_name) -> List[str]:
    # Return just the Default value.

        database_list = ['default']
        return database_list

    def get_tables(self, database_name, schema_name) -> List[GenericTable]:
    # Return all tables in a database provider.

        es = Elasticsearch(self.host,
           port=self.port,
           http_auth=(self.user, self.password),
           http_compress=True)
        
        dict_es = es.indices.get('*')
        dict_es_keys = dict_es.keys()

        generic_table_list = []
        table_list = meta_data.tables
        for idx in dict_es_keys:
            
            generic_table = GenericTable(idx)
            idx_fields = dict_es[idx]['mappings']['properties']
            for field in idx_fields.keys():

                column_type = idx_fields[field]['type']

                generic_table.add_column(GenericColumn(field, column_type))
            
            generic_table_list.append(generic_table)
        
        es.close()
        
        return generic_table_list
