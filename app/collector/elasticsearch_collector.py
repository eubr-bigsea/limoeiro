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

        
    def _process_object(
        self, database_name : str, idx_name : str,
        idx_type : TableType, obj : dict
    ) -> List[DatabaseTableCreateSchema]:
        """Process the matadata to get the tables objects."""
        
        tables : List[DatabaseTableCreateSchema] = []
        columns : List[TableColumnCreateSchema] = []
            
        # Iter all attributes
        for field, value in obj.items():
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
                tables += self._process_object(database_name, f"{idx_name}.{field}", TableType.LOCAL, value["properties"])

            # Get the types
            data_type_str = SQLTYPES_DICT[value_type.upper()]
            array_data_type_str = SQLTYPES_DICT[array_type.upper()] if array_type is not None else None 
            
            # Create the column object
            columns.append(
                            TableColumnCreateSchema(
                                name=field,
                                display_name=field,
                                data_type=data_type_str,
                                array_data_type = array_data_type_str
                            )
                    )

        # Create the table object
        tables.append( DatabaseTableCreateSchema(
                            name=idx_name,
                            display_name=idx_name,
                            fully_qualified_name=f"{database_name}.{idx_name}",
                            database_id=DEFAULT_UUID,
                            columns=columns,
                            type=idx_type
                       )
        )
        return tables

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
                tables += self._process_object(database_name, idx, TableType.REGULAR, value["mappings"]["properties"])

        # Close Connection
        es.close()

        return tables 

    def get_samples(self, database_name: str,
                    schema_name: str, table: DatabaseTableCreateSchema
    ) -> DatabaseTableSampleCreateSchema:
        """Return the samples from a column."""

        if table.type != TableType.LOCAL:
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

            es.close()

            return DatabaseTableSampleCreateSchema(
                                    date=datetime.now(),
                                    content=content,
                                    is_visible=True,
                                    database_table_id=DEFAULT_UUID,
            )
        else:
            return None
    
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

    # FIXME: Review
    def _get_schema_fqn_elements(
        self, provider_name, database_name, schema_name
    ) -> List[str]:
        """Return the elements of the schema fqn."""
        return []

    def _get_table_fqn_elements(
        self, provider_name, database_name, schema_name, table_name
    ) -> List[str]:
        """Return the elements of the table fqn."""
        return []

    def _get_database_fqn_elements(
        self, provider_name, database_name
    ) -> List[str]:
        """Return the elements of the database fqn."""
        return []

    def get_schemas(
        self, database_name: Optional[str] = None
    ) -> List[DatabaseSchemaCreateSchema]:
        return []


