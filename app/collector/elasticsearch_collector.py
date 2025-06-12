from typing import List,Optional
import typing
from datetime import datetime
from app.collector.collector import Collector
from app.collector import DEFAULT_UUID
from elasticsearch import Elasticsearch
from app.collector.utils.constants_utils import SQLTYPES_DICT
from app.models import DataType, TableType
from app.schemas import (
    DatabaseSchemaCreateSchema,
    DatabaseCreateSchema,
    DatabaseTableCreateSchema,
    TableColumnCreateSchema,
    DatabaseTableSampleCreateSchema,

)

class ElasticsearchCollector(Collector):
    """Class to implement methods, to collect data in Elasticsearch."""

    def __init__(self):
        super().__init__()

    def _get_column_name(self, column: str, super_column: str):
        return f"{super_column}>{column}" if super_column else column
    
    def _process_object(
        self, database_name : str,
        obj : dict, super_column: str = None
    ) -> List[TableColumnCreateSchema]:
        """Process the matadata to get the columns objects."""
        
        columns : List[TableColumnCreateSchema] = []
            
        # Iter all attributes
        for field, value in obj.items():
            column_name = self._get_column_name(field, super_column)
            
            value_type = None
            array_type = None
            # If the attribute 'type' exists, use it to determine the attribute's type.
            if 'type' in value:
                value_type = value['type']
                
                # If the type is 'nested', it is an array of objects
                if value_type == 'nested':
                    array_type = "object"
            else:
                # If the 'type' attribute is missing and the 'properties' attribute exists, it is an object.
                if 'properties' in value:
                    value_type = "object"

            # If the 'properties' attribute exists, it is an object, so process the object recursively.
            if 'properties' in value:

                
                columns += self._process_object(database_name,
                                               value["properties"],
                                               super_column = column_name)

            # Get the types
            data_type_str = SQLTYPES_DICT[value_type.upper()]
            array_data_type_str = SQLTYPES_DICT[array_type.upper()] if array_type is not None else None 
            
            # Create the column object
            table_column_object = TableColumnCreateSchema(
                            name=column_name,
                            display_name=column_name,
                            data_type=data_type_str,
                            array_data_type = array_data_type_str
                        )
            
            # Add the column object to the column list
            columns.append(table_column_object)

        return columns

    def get_tables(
        self, database_name: str, schema_name: str
    ) -> List[DatabaseTableCreateSchema]:
        """Return all tables in a database provider."""

        params = self.connection_info
        if params is None:
            raise ValueError("Connection parameters are not set.")
            
        # Connect to Elasticsearch
        es = Elasticsearch(
            params.host,
            port=params.port,
            http_auth=(params.user_name, params.password),
            http_compress=True,
        )

        # Get all index
        dict_es = es.indices.get("*")

        tables : List[DatabaseTableCreateSchema] = []
        
        # Iter all index
        for idx, value in dict_es.items():
            if "properties" in value["mappings"]:
                
                # Process the data
                columns = self._process_object(database_name, value["mappings"]["properties"])

                # Create the table object
                table_object = DatabaseTableCreateSchema(
                                name=idx,
                                display_name=idx,
                                fully_qualified_name=f"{database_name}.{idx}",
                                database_id=DEFAULT_UUID,
                                columns=columns,
                                type=TableType.REGULAR
                           )


                # Append the table object to the final list.
                tables.append(table_object)
                
        # Close Connection
        es.close()

        return tables 

    def _flatten_json(self, obj, super_column: str = None):
        """Return the flattened json of the samples from a column."""

        result_dict = {}
        # Iterate the object
        for key, items in obj.items():
            column_name = self._get_column_name(key, super_column)

            # If the attribute is an object, process it recursively
            if isinstance(items, dict):
                sub_dict = self._flatten_json(items, super_column = column_name)
                result_dict = result_dict | sub_dict

            # If the attribute is a list
            elif isinstance(items, list) and len(items) > 0:
                # If the list type is an object, process it recursively
                if isinstance(items[0], dict):
                    sub_dict = self._flatten_json(items[0], super_column = column_name)
                    result_dict = result_dict | sub_dict
                else:
                    result_dict[column_name] = items[0]

            else:
                result_dict[column_name] = items
                
        return result_dict
    
    def get_samples(self, database_name: str,
                    schema_name: str, table: DatabaseTableCreateSchema
    ) -> DatabaseTableSampleCreateSchema:
        """Return the samples from a column."""

        params = self.connection_info
        if params is None:
            raise ValueError("Connection parameters are not set.")

        es = Elasticsearch(
            params.host,
            port=params.port,
            http_auth=(params.user_name, params.password),
            http_compress=True,
        )

        index_name = table.name

        # Perform the search for the top 10 documents
        response = es.search(
            index=index_name,
            body={
                "size": 10,
                "query": {
                    "match_all": {}
                }
            }
        )

        # Get the documents
        content = [hit["_source"] for hit in response["hits"]["hits"]]        
        flattened_json = [self._flatten_json(obj) for obj in content]

        es.close()

        return DatabaseTableSampleCreateSchema(
                                date=datetime.now(),
                                content=flattened_json,
                                is_visible=True,
                                database_table_id=DEFAULT_UUID,
        )
    
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

    def supports_database(self) -> bool:
        return False

    def get_schemas(
        self, database_name: Optional[str] = None
    ) -> List[DatabaseSchemaCreateSchema]:
        return []


