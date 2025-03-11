
from app.collector.druid_collector import DruidCollector
from app.collector.hive_collector import HiveCollector
from app.collector.postgre_sql_collector import PostgreSqlCollector
from app.collector.elasticsearch_collector import ElasticsearchCollector

from app.collector.utils.request_utils import (
    get_request
)
import app.collector.utils.constants_utils as constants

class CollectorFactory:
# Class to create a collector based on database provider.

    @staticmethod
    def create_collector(provider):
    # Create a collector based on database provider.
        p_type_name = provider['provider_type']["display_name"]
        _, connection = get_request (constants.CONNECTION_ROUTE, provider["connection_id"])
        user = connection["user_name"]
        password = connection["password"]
        host = connection["host"]
        port = connection["port"]

        if p_type_name == "HIVE":
            return HiveCollector(user, password, host, port)

        elif p_type_name == "POSTGRESQL":
            return PostgreSqlCollector(user, password, host, port)

        elif p_type_name == "DRUID":
            return DruidCollector(user, password, host, port)
        
        elif p_type_name == "ELASTICSEARCH":
            return ElasticsearchCollector(user, password, host, port)

        else:
            raise ValueError(f"The collector for the <{p_type_name}> provider type is not supported.")