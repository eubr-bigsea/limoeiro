from typing import List,Optional
import typing
import math
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
from collections import defaultdict, Counter

class MongoCollector(Collector):
    """Class to implement methods, to collect data in Mongo."""

    def __init__(self):
        super().__init__()

    def _bson_to_python(self, obj):
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
            return {k: self._bson_to_python(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._bson_to_python(i) for i in obj]
        else:
            return obj

    def _process_object(self, obj):
        """ Process the object to get the metadata."""
        types_columns = defaultdict()
        types_columns_array = defaultdict()
        sub_tables = defaultdict()
        
        # Iter the object
        for key, value in obj.items():

            # Get the type of the attribute
            types_columns[key] = type(value)

            # If the attribute is an object, process it recursively
            if isinstance(value, dict):
                sub_tables[key] = self._process_object(value)

            # If the attribute is an array
            elif isinstance(value, list):
                # Get the most common type among all the values
                data = [type(i) for i in value if i is not None]
                most_common = Counter(data).most_common(1)
                most_common_type = most_common[0][0]
                types_columns_array[key] = most_common_type
                
                # If the most common type of the array is an object, process it recursively
                if most_common_type == dict:
                    # Get an object with the most common type
                    value_mask = [type(i) == most_common_type for i in value]
                    value_most_common_type = [v for v, m in zip(value, value_mask) if m][0]
                    # Process recursively
                    sub_tables[key] = self._process_object(value_most_common_type)

        return {
            "types_columns": types_columns,
            "types_columns_array": types_columns_array,
            "sub_tables": sub_tables
        }


    def _infer_metadata(self, collection, sample_size):
        """Infer metadata by sampling."""
        samples_type = []
        metadata = defaultdict(list)
        types_columns = defaultdict()
        types_columns_array = defaultdict()
        sub_tables = defaultdict()

        # Iter the samples to get the metadata of each sample
        for doc in collection.find().limit(sample_size):
            object_data = self._bson_to_python(doc)
            samples_type.append(self._process_object(object_data))


        # Iter all samples metada to aggregate them
        for sample in samples_type:
            for column, c_type in sample["types_columns"].items():
                metadata[column].append(c_type)


        # Iter all aggredated matadate to get the most common type
        for key, value in metadata.items():
            # Get all not None value
            data = [i for i in value if i is not None]
            # If there is no not None value, set a single None value            
            if len(data) == 0:
                data = [type(None)]

            # Get the most common type from all samples
            most_common = Counter(data).most_common(1)
            most_common_type = most_common[0][0]
            types_columns[key] = most_common_type
            
            type_array = None
            # If the most common type is a list
            if most_common_type == list:
                for sample in samples_type:
                    if key in sample["types_columns_array"]:
                        # Get the list type
                        type_array  = sample["types_columns_array"][key]
                        types_columns_array[key] = sample["types_columns_array"][key]
                        break

            # If the most common type is a dict or list of dict
            if ((most_common_type == dict) or (type_array == dict)):
                for sample in samples_type:
                    # Check if there is a sub table for this attribute
                    if key in sample["sub_tables"]:
                        # Get an example the sub table
                        sub_tables[key] = sample["sub_tables"][key]
                        break


        return {
            "types_columns": types_columns,
            "types_columns_array": types_columns_array,
            "sub_tables": sub_tables
        }

    def _create_tables(self, database_name, table_name, metadata, table_type: TableType
    ) -> List[DatabaseTableCreateSchema]:
        """Process the matadata to get the tables objects."""

        tables: typing.List[DatabaseTableCreateSchema] = []
        columns: typing.List[TableColumnCreateSchema] = []
        
        # Iter all attributes
        for column, c_type in metadata["types_columns"].items():

            # Get the type
            data_type_str = SQLTYPES_DICT [
                c_type.__name__.upper()
            ]
            data_type = DataType[data_type_str]

            # If the type is list, get the type inside the list
            array_data_type = None
            arr_c_type = None
            if c_type == list:
                arr_c_type = metadata["types_columns_array"][column]
                arr_data_type_str = SQLTYPES_DICT[
                    arr_c_type.__name__.upper()
                ]
                array_data_type = DataType[arr_data_type_str]

            # Create the column object
            columns.append(
                    TableColumnCreateSchema(
                        name=column,
                        display_name=column,
                        data_type=data_type,
                        array_data_type = array_data_type
                    )
            )
            
            # If the type is an object or the type inside the array is an object, process it recursively.
            # The inner levels of the recursion have type = LOCAL.
            if ((c_type == dict) or (arr_c_type == dict)):
                
                # Append the returned tables to the final list.
                tables += self._create_tables(database_name,
                                              f"{table_name}.{column}", 
                                              metadata["sub_tables"][column],
                                              TableType.LOCAL)

        # Create the table object
        database_table = DatabaseTableCreateSchema(
                    name=table_name,
                    display_name=table_name,
                    fully_qualified_name=f"{database_name}.{table_name}",
                    database_id=DEFAULT_UUID,
                    columns=columns,
                    type=table_type
                )
        
        # Append the table object to the final list.
        tables.append(database_table)

        return tables
    
    
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
            
            # Infer metadata by sampling
            metadata = self._infer_metadata(collection, sample_size)
            
            # Process the matadata to get the tables objects.
            # The first level of the recursion has type = REGULAR.
            tables += self._create_tables(database_name, collection_name, metadata, TableType.REGULAR)

        return tables

    def get_samples(self, database_name: str,
                    schema_name: str, table: DatabaseTableCreateSchema
    ) -> DatabaseTableSampleCreateSchema:
        """Return the samples from a column."""

        if table.type != TableType.LOCAL:
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
            collection = db[table.name]
            content = collection.find().limit(10)
            content = list(content)

            def sanitize_json(obj):
                if isinstance(obj, ObjectId):
                    return str(obj)
                if isinstance(obj, float) and math.isnan(obj):
                    return None
                if isinstance(obj, dict):
                    return {k: sanitize_json(v) for k, v in obj.items()}
                if isinstance(obj, list):
                    return [sanitize_json(v) for v in obj]
                return obj


            cleaned_data = sanitize_json(content)      

            return DatabaseTableSampleCreateSchema (
                                    date=datetime.datetime.now(),
                                    content=cleaned_data,
                                    is_visible=True,
                                    database_table_id=DEFAULT_UUID,
            )

        else:
            return None
    
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


