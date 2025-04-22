import typing
from app.collector.collector import Collector
from app.collector.druid_collector import DruidCollector
from app.collector.elasticsearch_collector import ElasticsearchCollector
from app.collector.hive_collector import HiveCollector
from app.collector.mariadb_collector import MariaDbCollector
from app.collector.mssql_collector import SqlServerCollector
from app.collector.oracle_collector import OracleCollector
from app.collector.postgres_collector import PostgresCollector
from app.schemas import (
    DatabaseProviderConnectionItemSchema,
    DatabaseProviderIngestionItemSchema,
    DatabaseProviderItemSchema,
)

from . import DatabaseProviderTypeDisplayName as SUPPORTED_TYPES


class CollectorFactory:
    """Class to create a collector based on database provider."""

    @staticmethod
    def create_collector(
        provider: DatabaseProviderItemSchema,
        ingestion: DatabaseProviderIngestionItemSchema,
        connection: DatabaseProviderConnectionItemSchema,
    ) -> Collector:
        """Create a collector based on database provider."""
        
        if (
            provider.provider_type is not None
            and provider.provider_type.id is not None
        ):
            p_type_name = provider.provider_type.id
        else:
            p_type_name = "UNKNOWN"
        
        collectors: typing.Dict[str, type[Collector]] = {
            SUPPORTED_TYPES.HIVE.value: HiveCollector,
            SUPPORTED_TYPES.POSTGRESQL.value: PostgresCollector,
            SUPPORTED_TYPES.DRUID.value: DruidCollector,
            SUPPORTED_TYPES.ELASTICSEARCH.value: ElasticsearchCollector,
            SUPPORTED_TYPES.MARIADB.value: MariaDbCollector,
            SUPPORTED_TYPES.MYSQL.value: MariaDbCollector,
            SUPPORTED_TYPES.SQLSERVER.value: SqlServerCollector,
            SUPPORTED_TYPES.ORACLE.value: OracleCollector,
        }

        collector_class = collectors.get(p_type_name)
        if collector_class:
            collector = collector_class()
            collector.ingestion = ingestion
            collector.connection_info = connection
            return collector
        else:
            raise ValueError(
                f"The collector for the <{p_type_name}> provider type "
                "is not supported."
            )
