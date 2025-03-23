from app.collector.collector import Collector
from app.collector.druid_collector import DruidCollector
from app.collector.elasticsearch_collector import ElasticsearchCollector
from app.collector.hive_collector import HiveCollector
from app.collector.mariadb_collector import MariaDbCollector
from app.collector.postgres_collector import PostgresCollector
from app.schemas import DatabaseProviderItemSchema

from . import DatabaseProviderTypeDisplayName as SUPPORTED_TYPES


class CollectorFactory:
    """Class to create a collector based on database provider."""

    @staticmethod
    def create_collector(provider: DatabaseProviderItemSchema) -> Collector:
        """Create a collector based on database provider."""
        if (
            provider.provider_type is not None
            and provider.provider_type.id is not None
        ):
            p_type_name = provider.provider_type.id
        else:
            p_type_name = "UNKNOWN"

        collectors = {
            SUPPORTED_TYPES.HIVE.value: HiveCollector,
            SUPPORTED_TYPES.POSTGRESQL.value: PostgresCollector,
            SUPPORTED_TYPES.DRUID.value: DruidCollector,
            SUPPORTED_TYPES.ELASTICSEARCH.value: ElasticsearchCollector,
            SUPPORTED_TYPES.MARIADB.value: MariaDbCollector,
        }
        collector_class = collectors.get(p_type_name)
        if collector_class:
            return collector_class(None, None, None, None)
        else:
            raise ValueError(
                f"The collector for the <{p_type_name}> provider type "
                "is not supported."
            )
