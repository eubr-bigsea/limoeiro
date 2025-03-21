
import logging
from datetime import datetime
import json
from app.collector.utils.request_utils import (
    post_request,
    patch_request,
    get_request
)
from app.collector.utils.cron_utils import (
    check_if_cron_is_today
)


import app.collector.utils.constants_utils as constants
from app.collector.collector import (Collector, GenericTable)
from app.collector.collector_factory import CollectorFactory
from app.collector.data_collection_logging import DataCollectionLogging
from app.collector.data_collection_diff_checker import DataCollectionDiffChecker

import os

class DataCollectionEngine():
    """ Class to implement the collection data engine. """

    def __init__(self):
        self.log = DataCollectionLogging()
        self.diff = DataCollectionDiffChecker(self.log)

    def _format_fully_qualified_name (self, list_values):
        """ Format the fully qualified name. """
        fully_qualified_name = list_values
        fully_qualified_name = [f.lower().replace(" ", "_") for f in fully_qualified_name]
        return ".".join(fully_qualified_name)

    def _process_object (self, route, f_q_name, new_dict):   
        """ Process an object generically using the Limoeiro API. """
        f_q_route = route+"/"+constants.F_Q_NAME_ROUTE
        
        """ Get the object by the fully qualified name. """
        response_code, current_dict = get_request (f_q_route, f_q_name)

        if response_code == 404:
            """ If the object does not exist, create it using a post request. """
            return post_request (route, new_dict)
        else:
            """ If the object already exists, update it using a patch request. """
            result_dict = self.diff.diff_objects (new_dict, current_dict, route)
            return patch_request (route, result_dict["id"], result_dict)

    def _process_database (self, collector : Collector, database_name, domain, layer, provider):
        """ Process the object database. """
        fqn_elements = collector._get_database_fqn_elements(provider['name'], database_name)
        f_q_name = self._format_fully_qualified_name(fqn_elements)

        new_dict = {
          "name": database_name,
          "display_name": database_name,
          "description": database_name,
          "fully_qualified_name": f_q_name,
          "domain_id": domain['id'],
          "layer_id": layer['id'],
          "provider_id": provider['id']
        }

        self.log.log_obj_collecting('database', database_name)
        return self._process_object(constants.DATABASE_ROUTE, f_q_name, new_dict)

    def _process_schema (self, collector : Collector, schema_name, domain, layer, provider, database):
        """ Process the object schema. """
        fqn_elements = collector._get_schema_fqn_elements(provider['name'], database['name'], schema_name)
        f_q_name = self._format_fully_qualified_name(fqn_elements)

        new_dict = {
          "name": schema_name,
          "fully_qualified_name": f_q_name,
          "display_name": schema_name,
          "description": schema_name,
          "domain_id": domain['id'],
          "layer_id": layer['id'],
          "database_id": database['id']
        }

        self.log.log_obj_collecting('schema', schema_name)
        return self._process_object(constants.SCHEMA_ROUTE, f_q_name, new_dict)

    def _process_table (self, collector : Collector, generic_table : GenericTable, domain, layer, provider, database, schema):
        """ Process the object table. """
        fqn_elements = collector._get_table_fqn_elements(provider['name'], database['name'], schema['name'], generic_table.name)
        f_q_name = self._format_fully_qualified_name(fqn_elements)

        """ Assemble the columns of the table. """
        columns = []
        for column_obj in generic_table.columns:
            column_name = column_obj.name

            column_type = str(column_obj.type).upper()
            column_type = constants.SQLTYPES_DICT[column_type]

            primary_key = column_obj.primary_key
            nullable    = column_obj.nullable
            unique      = column_obj.unique
            is_metadata = 'metadata_' in column_name
            columns.append(
                {
                  "name": column_name,
                  "display_name": column_name,
                  "description": column_name,
                  "data_type": column_type,
                  "primary_key": primary_key,
                  "nullable": nullable,
                  "unique": unique,
                  "is_metadata": is_metadata
                }
            )

        new_dict = {
          "name": generic_table.name,
          "fully_qualified_name":  f_q_name,
          "display_name": generic_table.name,
          "description": generic_table.name,
          "type": "REGULAR",
          "domain_id": domain['id'],
          "layer_id": layer['id'],
          "database_id":  database['id'],
          "database_schema_id": schema['id'],
          "columns": columns
        }

        self.log.log_obj_collecting('table', generic_table.name)
        return self._process_object(constants.TABLE_ROUTE, f_q_name, new_dict)

    def _get_ingestions(self, page):
        """ Load the database provider ingestions. """
        dict_param = {"page":page, "page_size":20}
        _, result = get_request(constants.INGESTION_ROUTE, None, dict_param=dict_param)
        return result["items"], result["page"], result["page_count"]

    def _execute_collection(self, ingestion):
        """ Execute the collection for the database provider. """
        
        _, provider = get_request(constants.PROVIDER_ROUTE, ingestion['provider_id']) 
        domain = provider['domain']
        layer = provider['layer']

        """ Create the collector. """
        collector = CollectorFactory.create_collector(provider)

        """ Get the databases of the database provider. """
        database_list = collector.get_databases()

        """ Iterate all databases. """
        for dabase_name in database_list:

            """ Process the object database """
            database = self._process_database(collector, dabase_name, domain, layer, provider)

            """ Get the schemas of the database. """
            schema_list = collector.get_schemas(dabase_name)

            """ Iterate all schemas. """
            for schema_name in schema_list:

                """ Process the object schema """
                schema = self._process_schema(collector, schema_name, domain, layer, provider, database)

                """ Get the tables of the schema. """
                table_list = collector.get_tables(dabase_name, schema_name)

                """ Iterate all tables. """
                for generic_table in table_list:

                    """ Process the object table. """
                    table = self._process_table(collector, generic_table, domain, layer, provider, database, schema)

    def execute_engine(self):
        """ Execute the collection data engine. """
        current_page = 0
        page_count = None
        
        """ Iter until last page. """
        while (current_page != page_count):
            """ Get all database providers with pagination. """
            current_page += 1
            ingestions, page, page_count = self._get_ingestions(current_page)

            """ Iterate the database providers. """
            for i in ingestions:

                cron_expression = None
                if (('scheduling' in i) and ('expression' in i['scheduling'])):
                    cron_expression = i['scheduling']['expression']

                """ Check if the cron expression should be executed today. """
                if check_if_cron_is_today(cron_expression):
                    self._execute_collection(i)
                else:
                    """ If not, skip to the next iteration. """
                    self.log.log_provider_skipped(i['display_name'])
