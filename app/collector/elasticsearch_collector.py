from typing import List,Optional
import typing

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

    def get_tables(
        self, database_name: str, schema_name: str
    ) -> List[DatabaseTableCreateSchema]:
        """Return all tables in a database provider."""

        params = self.connection_info
        if params is None:
            raise ValueError("Connection parameters are not set.")
        es = Elasticsearch(
            params.host,
            port=params.port,
            http_auth=(params.user_name, params.password),
            http_compress=True,
        )

        dict_es = es.indices.get("*")
        dict_es_keys = dict_es.keys()

        tables = []
        for idx in dict_es_keys:
            if "properties" in  dict_es[idx]["mappings"]:
                idx_fields = dict_es[idx]["mappings"]["properties"]

                columns: typing.List[TableColumnCreateSchema] = []
                for field in idx_fields.keys():
                    data_type_str = SQLTYPES_DICT[
                        idx_fields[field]["type"].upper()
                    ]
                    columns.append(
                            TableColumnCreateSchema(
                                name=field,
                                display_name=field,
                                data_type=DataType[data_type_str]
                            )
                    )
                name = idx
                database_table = DatabaseTableCreateSchema(
                            name=name,
                            display_name=name,
                            fully_qualified_name=f"{database_name}.{name}",
                            database_id=DEFAULT_UUID,
                            columns=columns,
                            type=TableType.REGULAR
                        )
                tables.append(database_table)

        es.close()

        return tables

    def get_samples(self, database_name: str,
                    schema_name: str, table_name: str
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
        
        index_name = table_name

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
                                sample_date=datetime.now(),
                                content=content,
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


