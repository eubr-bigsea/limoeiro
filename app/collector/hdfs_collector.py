from typing import List,Optional
import typing

from app.collector.collector import Collector
from app.collector import DEFAULT_UUID

import pyarrow as pa
import pyarrow.parquet as pq
import requests
import re
from app.collector.utils.constants_utils import SQLTYPES_DICT
from app.models import DataType, TableType
from app.schemas import (
    DatabaseSchemaCreateSchema,
    DatabaseCreateSchema,
    DatabaseTableCreateSchema,
    TableColumnCreateSchema,

)

FILE_PATTERN = "part-\d{5}-.*"

class HdfsCollector(Collector):
    """Class to implement methods, to collect data in HDFS."""

    def __init__(self):
        super().__init__()

    def _check_file(self, url, username):
        """Check if there is only one file in the directory."""
        params = {
            "user.name": username,
            "op":"LISTSTATUS"
        }
        response = requests.get(url, params=params).json()
        elments = response['FileStatuses']['FileStatus']

        return ( \
                   all((e['type'] == 'FILE') for e in elments) and \
                   any((re.fullmatch(FILE_PATTERN, e['pathSuffix'])) for e in elments)
               )

    def _process_file(self, file, url, username, database_name):
        """Read a single file from the partitions."""

        params = {
            "user.name": username,
            "op":"LISTSTATUS"
        }
        url_host = url+file

        response = requests.get(url_host, params=params).json()
        file_name = None
        for e in response['FileStatuses']['FileStatus']:
            if (re.fullmatch(FILE_PATTERN, e['pathSuffix'])):
                file_name = e['pathSuffix']

        if file_name is None:
            ValueError("Failed to retrieve one of the Parquet file.")

        file_url = url_host+"/"+file_name

        params = {
            "user.name": username,
            "op":"OPEN"
        }
        response = requests.get(file_url, params=params)

        # Ensure the response contains binary data (check status and content type)
        if response.status_code == 200 and response.headers['Content-Type'] == 'application/octet-stream':
            binary_data = response.content  # This is the binary data

            # Create a pyarrow BufferReader from the binary data
            buffer = pa.BufferReader(binary_data)

            # Load the Parquet file
            parquet_file = pq.ParquetFile(buffer)

            schema = parquet_file.schema
            columns: typing.List[TableColumnCreateSchema] = []
            for i in schema:
                logical_type = str(i.logical_type).upper()
                logical_type = re.sub(r"\s*\([^)]*\)", "", logical_type)

                data_type_str = SQLTYPES_DICT[
                    logical_type
                ]
                data_type = DataType[data_type_str]
                    
                columns.append(
                        TableColumnCreateSchema(
                            name=i.name,
                            display_name=i.name,
                            data_type=data_type
                        )
                )

            database_table = DatabaseTableCreateSchema(
                name=file,
                display_name=file,
                fully_qualified_name=f"{database_name}.{file}",
                database_id=DEFAULT_UUID,
                columns=columns,
                type=TableType.REGULAR
            )
            self._tables.append(database_table)   

        else:
            ValueError("Failed to retrieve the Parquet file or it is not binary.")

    def _open_directory(self, file, url, username, database_name):
        """Navigate through a directory."""

        file_str = ""
        if file is not None:
            file_str = file
        
        url_host = url+file_str

        # Check if there is only one files in the directory.
        if self._check_file(url_host, username):
            # Read a single file from the partitions.
            self._process_file(file_str, url, username, database_name)
        else:
            # List and navigate through the directory.
            params = {
                "user.name": username,
                "op":"LISTSTATUS"
            }
            response = requests.get(url_host, params=params).json()
            elments = response['FileStatuses']['FileStatus']
            for elment in response['FileStatuses']['FileStatus']:
                if elment['type'] == 'DIRECTORY':
                    # List and navigate through the directory recursively.
                    self._open_directory(file_str+"/"+elment['pathSuffix'], url, username, database_name)

    def get_tables(
        self, database_name: str, schema_name: str
    ) -> List[DatabaseTableCreateSchema]:
        """Return all tables in a database provider."""

        params = self.connection_info
        if params is None:
            raise ValueError("Connection parameters are not set.")
        
        username = params.user_name
        host = params.host
        port = params.port
        database = params.database

        url = f"http://{host}:{port}/webhdfs/v1/{database}/"
        
        self._tables = []
        self._open_directory(None, url, username, database_name)
        
        return self._tables

    def get_samples(self, database_name: str,
                    schema_name: str, table_name: str
    ) -> DatabaseTableSampleCreateSchema:
        """Return the samples from a column."""

        params = self.connection_info
        if params is None:
            raise ValueError("Connection parameters are not set.")
        
        username = params.user_name
        host = params.host
        port = params.port
        database = params.database

        url = f"http://{host}:{port}/webhdfs/v1/{database_name}/{table_name}"
        params = {
            "user.name": username,
            "op":"OPEN"
        }
        response = requests.get(url, params=params)
        content = None
        # Ensure the response contains binary data (check status and content type)
        if response.status_code == 200 and response.headers['Content-Type'] == 'application/octet-stream':
            binary_data = response.content  # This is the binary data

            # Create a pyarrow BufferReader from the binary data
            buffer = pa.BufferReader(binary_data)

            # Load the Parquet file
            parquet_file = pq.ParquetFile(buffer)

            table = parquet_file.read()  
            df = table.to_pandas()
            content = df.head(10).to_dict(orient="records")    
                
            
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

        name = params.database
        return [DatabaseCreateSchema(
                name=name,
                display_name=name,
                fully_qualified_name="placeholder",
                provider_id=DEFAULT_UUID,
            )]

    def supports_database(self):
        return False

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


