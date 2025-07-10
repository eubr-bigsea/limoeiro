import datetime
import os
import re
import typing
import uuid
import requests
from collections import defaultdict

from app.collector.collector import Collector
import app.collector.utils.constants_utils as constants
from app.collector.collector_factory import CollectorFactory
from app.collector.data_collection_diff_checker import DataCollectionDiffChecker
from app.collector.data_collection_logging import DataCollectionLogging
from app.collector.utils.api_client import (
    AssetApiClient,
    DatabaseApiClient,
    DatabaseTableApiClient,
    DatabaseProviderApiClient,
)
from app.collector.utils.cron_utils import check_if_cron_is_today
from app.collector.utils.request_utils import (
    get_request,
    options_request,
    patch_request,
    post_request,
    custom_serializer,
)
from app.schemas import (
    DatabaseCreateSchema,
    DatabaseItemSchema,
    DatabaseProviderConnectionItemSchema,
    DatabaseProviderIngestionItemSchema,
    DatabaseProviderItemSchema,
    DatabaseSchemaCreateSchema,
    DatabaseSchemaItemSchema,
    DatabaseTableCreateSchema,
    DatabaseTableItemSchema,
    DatabaseTableSampleCreateSchema,
    DatabaseTableSampleItemSchema,
)

FQN_PREFIXES = {
    "DatabaseProvider": "pvr",
    "Database": "db",
    "Schema": "schm",
    "Table": "tb",
}


class DataCollectionEngine:
    """Class to implement the collection data engine."""

    def __init__(self):
        self.log = DataCollectionLogging()
        self.diff = DataCollectionDiffChecker(self.log)

    def _format_fqn(self, asset_type: str, list_values: typing.List):
        """Format the fully qualified name."""
        fully_qualified_name = [
            f.lower().replace(" ", "_").replace(".", "-") for f in list_values
        ]
        return f"{FQN_PREFIXES[asset_type]}." + ".".join(fully_qualified_name)

    def _process_sample(self, 
                        database_table_sample: DatabaseTableSampleCreateSchema):
        response_code, response = get_request(constants.SAMPLE_ROUTE,f"table/{database_table_sample.database_table_id}")

        if response_code == 404:
            return post_request(constants.SAMPLE_ROUTE, database_table_sample.model_dump()) 
        elif response_code == 200:
            response = DatabaseTableSampleItemSchema.model_validate(response)
            return patch_request(
                constants.SAMPLE_ROUTE, str(response.id), database_table_sample.model_dump()
            )
        else:
            raise Exception(f"Invalid status {response_code}")

    def _process_object(
        self,
        route: str,
        fqn: str,
        new_asset: typing.Union[
            DatabaseProviderItemSchema,
            DatabaseCreateSchema,
            DatabaseSchemaCreateSchema,
            DatabaseTableCreateSchema,
        ],
    ):
        """Process an object generically using the Limoeiro API."""

        # Get the object by the fully qualified name.
        response_code, _ = options_request(constants.ASSET_ROUTE, fqn)

        if response_code == 404:
            # If the object does not exist, create it using a post request.
            return post_request(route, new_asset.model_dump())
        elif response_code == 200:
            # If the object already exists, update it using a patch request.
            # FIXME result_dict = self.diff.diff_objects(new_asset, current_dict, route)
            new_asset.version = "1"
            new_asset.updated_at = datetime.datetime.utcnow()
            return patch_request(
                route, new_asset.fully_qualified_name, new_asset.model_dump()
            )
        else:
            raise Exception(f"Invalid status {response_code}")

    def _process_database(
        self,
        database: DatabaseCreateSchema,
        provider: DatabaseProviderItemSchema,
    ):
        """Process the object database."""
        fqn = self._format_fqn("Database", [provider.name, database.name])

        database.fully_qualified_name = fqn
        database.provider_id = provider.id

        self.log.log_obj_collecting("database", database.name)

        result: typing.Dict[str, typing.Any] = self._process_object(
            constants.DATABASE_ROUTE, fqn=fqn, new_asset=database
        )
        return DatabaseItemSchema(**result)

    def _process_schema(
        self,
        schema: DatabaseSchemaCreateSchema,
        provider,
        database,
    ) -> DatabaseSchemaItemSchema:
        """Process the object schema."""
        fqn = self._format_fqn(
            "Schema", [provider.name, database.name, schema.name]
        )
        schema.fully_qualified_name = fqn
        schema.database_id = database.id
        self.log.log_obj_collecting("schema", schema.name)
        return DatabaseSchemaItemSchema(
            **self._process_object(constants.SCHEMA_ROUTE, fqn, schema)
        )

    def _process_table(
        self,
        table: DatabaseTableCreateSchema,
        provider: DatabaseProviderItemSchema,
        database: DatabaseItemSchema,
        schema: typing.Optional[DatabaseSchemaItemSchema],
    ):
        """Process the object table."""
        list_values = [
            provider.name,
            database.name,
            schema.name if schema else None,
            table.name,
        ]
        # Remove None values
        list_values = [item for item in list_values if item is not None]

        fqn = self._format_fqn(
            "Table",
            list_values,
        )
        table.fully_qualified_name = fqn
        table.database_id = database.id
        if schema is not None:
            table.database_schema_id = schema.id

        self.log.log_obj_collecting("table", table.name)
        return DatabaseTableItemSchema.model_validate(self._process_object(constants.TABLE_ROUTE, fqn, table))

    def execute_collection(
        self,
        provider: DatabaseProviderItemSchema,
        connection: DatabaseProviderConnectionItemSchema,
        ingestion: DatabaseProviderIngestionItemSchema,
    ):
        """Execute the collection for the database provider."""
        
        # Create the collector.
        collector = CollectorFactory.create_collector(
            provider, ingestion, connection
        )
        # Get the databases of the database provider.
        database_list = collector.get_databases()
        include_db_re = (
            re.compile(ingestion.include_database)
            if ingestion.include_database
            else None
        )
        exclude_db_re = (
            re.compile(ingestion.exclude_database)
            if ingestion.exclude_database
            else None
        )
        include_sc_re = (
            re.compile(ingestion.include_schema)
            if ingestion.include_schema
            else None
        )
        exclude_sc_re = (
            re.compile(ingestion.exclude_schema)
            if ingestion.exclude_schema
            else None
        )
        include_tb_re = (
            re.compile(ingestion.include_table)
            if ingestion.include_table
            else None
        )
        exclude_tb_re = (
            re.compile(ingestion.exclude_table)
            if ingestion.exclude_table
            else None
        )
        # Iterate all databases.
        ignored_dbs = []
        valid_dbs = []
        for db in database_list:
            db_name = db.name
            if collector.supports_database():
                # Test if db_name must be excluded from processing (ignored)
                must_not_db = bool(exclude_db_re and exclude_db_re.match(db_name))
                # Test if db_name must be processed
                must_db = bool(include_db_re and include_db_re.match(db_name))
                # If both flags, item is explicitly ignored
                ignore_db = (include_db_re is not None and not must_db) or must_not_db
            else:
                ignore_db = False
                must_db   = True
                
            if ignore_db:
                ignored_dbs.append(db_name)
            elif must_db:
                # Process the object database
                database = self._process_database(db, provider)
                valid_dbs.append(db_name)
                
                # Get the schemas of the database.

                if collector.supports_schema():
                    schema_list = collector.get_schemas(db_name)

                    ignorable = collector.get_ignorable_schemas()
                    # Iterate all schemas.
                    for schema in schema_list:
                        schema_name = schema.name
                        if schema_name in ignorable:
                            continue
                        
                        must_not_sc = bool(exclude_sc_re and exclude_sc_re.match(schema_name))
                        must_sc = bool(include_sc_re and include_sc_re.match(schema_name))
                        ignore_sc = (include_sc_re is not None and not must_sc) or must_not_sc
                        
                        if ignore_sc:
                            print(f"Schema '{schema_name}' ignored by rules.")
                            continue
                        
                        # Process the object schema
                        schema = self._process_schema(
                            schema, provider, database
                        )

                        table_list = collector.get_tables(db_name, schema_name)
                    
                        schema_ignored_tbs = []
                        schema_valid_tbs = []

                        for table in table_list:
                            self._pre_process_table(
                                table,
                                provider,
                                include_tb_re,
                                exclude_tb_re,
                                database,
                                collector,
                                ingestion,
                                schema_ignored_tbs,  # ou ignored_tbs
                                schema_valid_tbs,    # ou valid_tbs
                                schema               # ou None se não houver schema
                            )
                        
                        db_table_api_client = DatabaseTableApiClient()
                        existing_tbs_in_database = db_table_api_client.find_by_database(str(database.id))
                        
                        existing_tbs_in_schema = [
                            tb for tb in existing_tbs_in_database 
                            if tb.database_schema and str(tb.database_schema.id) == str(schema.id)
                        ]
                        names_to_disable = []
                        tb_ids_to_disable = []

                        for tb in existing_tbs_in_schema:
                            if tb.name not in schema_valid_tbs:
                                tb_ids_to_disable.append(tb.id)
                                names_to_disable.append(tb.name)
                        if tb_ids_to_disable:
                            self.log.log.info(
                                "Tables(s) present in metadata under schema '%s' that will be disabled: [%s]",
                                schema_name, ", ".join(names_to_disable),
                            )
                        AssetApiClient.disable_many(tb_ids_to_disable)

                        if schema_ignored_tbs:
                            self.log.log.info(
                                "Table(s) under schema '%s' ignored by the rules: [%s]",
                                schema_name, ", ".join(schema_ignored_tbs),
                            )
                                
                else: 
                    
                    ignored_tbs = []
                    valid_tbs = []
                    table_list = collector.get_tables(db_name, db_name) 
                    for table in table_list:
                        self._pre_process_table(
                            table,
                            provider,
                            include_tb_re,
                            exclude_tb_re,
                            database,
                            collector,
                            ingestion,
                            ignored_tbs,  
                            valid_tbs,    
                            None             
                        )
                    db_client = DatabaseTableApiClient()
                    existing_tbs = db_client.find_by_database(str(database.id))
                    names_to_disable = []
                    tb_to_disable = []

                    for tb in existing_tbs:
                        if tb.name not in valid_tbs:
                            tb_to_disable.append(tb.id)
                            names_to_disable.append(tb.name)
                    if tb_to_disable:
                        self.log.log.info(
                            "Tables(s) present in metadata that will be disabled: [%s]",
                            ", ".join(names_to_disable),
                        )
                    AssetApiClient.disable_many(tb_to_disable)

                    if ignored_tbs:
                        self.log.log.info(
                            "Table(s) ignored by the rules: [%s]",
                            ", ".join(ignored_tbs),
                        )
        else:
            db_client = DatabaseApiClient()
            existing_dbs = db_client.find_by_provider(str(provider.id))
            names_to_disable = []
            to_disable = []
            for db in existing_dbs:
                if db.name not in valid_dbs:
                    to_disable.append(db.id)
                    names_to_disable.append(db.name)
            if to_disable:
                self.log.log.info(
                    "Database(s) present in metadata that will be disabled: [%s]",
                    ", ".join(names_to_disable),
                )
            AssetApiClient.disable_many(to_disable)

        if ignored_dbs:
            self.log.log.info(
                "Database(s) ignored by the rules: [%s]", ", ".join(ignored_dbs)
            )

    def _get_semantic_type(self, sample:typing.List) -> str:
        sample_serialized = []
        for s in sample:
            if isinstance(s, uuid.UUID):
                sample_serialized.append(str(s))
            elif isinstance(s, datetime.datetime):
                sample_serialized.append(s.isoformat())
            else:
                sample_serialized.append(str(s))

        api_url = os.environ["SEMANTIC_API_URL"]
        url = api_url.rstrip("/") + "/" + "classificar-valores/"
        response = requests.post(
            url, json=sample_serialized
        )
        
        if response.status_code == 200:
            return response.text.replace("\"", "") 
        else:
            return "API_FAILED"
        
    def _pre_process_table(
        self,
        table: DatabaseTableCreateSchema,
        provider: DatabaseProviderItemSchema,
        include_tb_re: typing.Optional[re.Pattern],
        exclude_tb_re: typing.Optional[re.Pattern],
        database: DatabaseItemSchema,
        collector: Collector,
        ingestion: DatabaseProviderIngestionItemSchema,
        ignored_tbs: typing.List[str],
        valid_tbs: typing.List[str],
        schema: typing.Optional[DatabaseSchemaItemSchema] = None,
    ):
        tb_name = table.name
        must_not_tb = bool(exclude_tb_re and exclude_tb_re.match(tb_name))
        must_tb = (include_tb_re is None) or (include_tb_re and include_tb_re.match(tb_name))
        ignore_tb = (not must_tb) or must_not_tb

        if ignore_tb:
            ignored_tbs.append(tb_name)
            self.log.log.info(f"Table '{tb_name}' ignored by rules.")
            return

        self.log.log.info(f"Table '{tb_name}' will be processed.")
        table.database_id = database.id
        if schema:
            table.database_schema_id = schema.id

        database_table_sample = None
        if ingestion.collect_sample:
            database_table_sample = collector.get_samples(
                database.name,
                schema.name if schema else database.name,
                table,
            )

            if ingestion.apply_semantic_analysis and database_table_sample and database_table_sample.content:
                structured_sample = defaultdict(list)
                for sample in database_table_sample.content:
                    for column in sample.keys():
                        structured_sample[column].append(sample[column])

                for column in table.columns:
                    sample = structured_sample.get(column.name, [])
                    if sample:
                        semantic_type = self._get_semantic_type(sample)
                        column.semantic_type = semantic_type

        table_return = self._process_table(
            table,
            provider,
            database,
            schema,
        )

        if database_table_sample:
            database_table_sample.database_table_id = table_return.id
            self._process_sample(database_table_sample)

        valid_tbs.append(tb_name)
