from typing import List,Optional
import typing

from app.collector.collector import Collector
from app.collector import DEFAULT_UUID
from pymongo import MongoClient
from collections import defaultdict
import bson
import datetime
from bson import ObjectId, Decimal128, Timestamp, Binary, Int64
from app.collector.utils.constants_utils import SQLTYPES_DICT
from app.models import DataType, TableType
from app.schemas import (
    DatabaseSchemaCreateSchema,
    DatabaseCreateSchema,
    DatabaseTableCreateSchema,
    TableColumnCreateSchema,
    DatabaseTableSampleCreateSchema,
)
from datetime import datetime

class MongoCollector(Collector):
    """Class to implement methods, to collect data in Mongo."""

    def __init__(self):
        super().__init__()

    def bson_to_python(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, Decimal128):
            return float(obj.to_decimal())
        elif isinstance(obj, Int64):
            return int(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, Timestamp):
            return obj.time
        elif isinstance(obj, Binary):
            return obj.decode('utf-8', errors='ignore')
        elif isinstance(obj, dict):
            return {k: self.bson_to_python(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.bson_to_python(i) for i in obj]
        else:
            return obj

        
    def infer_metadata(self, collection, sample_size):
        """Infer metadata by sampling."""
        types_columns = {}

        for doc in collection.find().limit(sample_size):
            for key, value in doc.items():
                if key not in types_columns:
                    types_columns[key] = set()

                obj = self.bson_to_python(value)
                types_columns[key].add(type(obj).__name__.upper())

        metadata = {}
        for column, types in types_columns.items():
            # If there is more than one element, remove the NoneType
            if len(types) > 1:
                none_type = type(None).__name__.upper()
                types.remove(none_type)

            metadata[column] = list(types)
        return metadata
        
    def get_tables(
        self, database_name: str, schema_name: str
    ) -> List[DatabaseTableCreateSchema]:
        """Return all tables in a database provider."""

        params = self.connection_info
        if params is None:
            raise ValueError("Connection parameters are not set.")
        
        username = params.user_name
        password = params.password
        host = params.host
        port = params.port

        uri = f"mongodb://{username}:{password}@{host}:{port}/"
        # Connect to Mongodb
        client = MongoClient(uri)
        db = client[database_name]
        # List all collections
        collection_names = db.list_collection_names()
        
        tables = []
        for collection_name in collection_names:

            db = client[database_name]
            collection = db[collection_name]

            # Amount of data to sample
            sample_size = 100
            metadata = self.infer_metadata(collection, sample_size)

            columns: typing.List[TableColumnCreateSchema] = []
            for column, types in metadata.items():
                first_type = types[0]
                data_type_str = SQLTYPES_DICT[
                    first_type
                ]
                data_type = DataType[data_type_str]
                    
                columns.append(
                        TableColumnCreateSchema(
                            name=column,
                            display_name=column,
                            data_type=data_type
                        )
                )

            database_table = DatabaseTableCreateSchema(
                        name=collection_name,
                        display_name=collection_name,
                        fully_qualified_name=f"{database_name}.{collection_name}",
                        database_id=DEFAULT_UUID,
                        columns=columns,
                        type=TableType.REGULAR
                    )
            tables.append(database_table)

        return tables

    def get_samples(self, database_name: str,
                    schema_name: str, table_name: str
    ) -> DatabaseTableSampleCreateSchema:
        """Return the samples from a column."""

        params = self.connection_info
        if params is None:
            raise ValueError("Connection parameters are not set.")
        
        username = params.user_name
        password = params.password
        host = params.host
        port = params.port

        uri = f"mongodb://{username}:{password}@{host}:{port}/"
        # Connect to Mongodb
        client = MongoClient(uri)
        db = client[database_name]
        collection = db[table_name]
        content = collection.find().limit(10)
        content = list(content)

        return DatabaseTableSampleCreateSchema(
                                sample_date=datetime.now(),
                                content=content,
                                is_visible=True,
                                database_table_id=DEFAULT_UUID,
        )
    
    def get_databases(self) -> List[DatabaseCreateSchema]:
        """Return all databases."""
       
        params = self.connection_info
        if params is None:
            raise ValueError("Connection parameters are not set.")
        
        username = params.user_name
        password = params.password
        host = params.host
        port = params.port

        uri = f"mongodb://{username}:{password}@{host}:{port}/"
        # Connect to Mongodb
        client = MongoClient(uri)
        
        # List all databases
        database_names = client.list_database_names()
        databases = []
        for name in database_names:
            databases.append(DatabaseCreateSchema(
                name=name,
                display_name=name,
                fully_qualified_name="placeholder",
                provider_id=DEFAULT_UUID,
            ))

        return databases

    def supports_schema(self):
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


