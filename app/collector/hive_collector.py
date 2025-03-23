from typing import List
from sqlalchemy.engine import create_engine

from app.collector.sql_alchemy_collector import SqlAlchemyCollector


class HiveCollector(SqlAlchemyCollector):
    """Class to implement methods, to collect data in HIVE."""

    def get_databases_names(self) -> List[str]:
        """Return just the Default value."""
        database_list = ["default"]
        return database_list

    def get_connection_engine_for_schemas(self, database_name: str):
        """Return the connection engine to get the schemas."""
        connection = (
            f"hive://{self.user}:{self.password}@{self.host}:{self.port}"
        )
        engine = create_engine(connection, connect_args={"auth": "LDAP"})
        return engine

    def get_connection_engine_for_tables(
        self, database_name: str, schema_name: str
    ):
        """Return the connection engine to get the tables."""
        connection = f"hive://{self.user}:{self.password}@{self.host}:{self.port}/{schema_name}"
        engine = create_engine(connection, connect_args={"auth": "LDAP"})
        return engine

    def _get_database_fqn_elements(
        self, provider_name, database_name
    ) -> List[str]:
        """Return the elements of the database fqn."""
        return [provider_name, database_name]

    def _get_schema_fqn_elements(
        self, provider_name, database_name, schema_name
    ) -> List[str]:
        """Return the elements of the schema fqn."""
        return [provider_name, database_name, schema_name]

    def _get_table_fqn_elements(
        self, provider_name, database_name, schema_name, table_name
    ) -> List[str]:
        """Return the elements of the table fqn."""
        return [provider_name, database_name, schema_name, table_name]
