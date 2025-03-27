from typing import List
from abc import ABC, abstractmethod
import typing

from app.schemas import (
    DatabaseCreateSchema,
    DatabaseProviderConnectionItemSchema,
    DatabaseProviderIngestionItemSchema,
    DatabaseSchemaCreateSchema,
    DatabaseTableCreateSchema,
)


class Collector(ABC):
    """Abstract Class to define methods to collect data in collection engine."""

    __slots__ = ('connection_info', 'ingestion')
    def __init__(self):
        self.connection_info: typing.Optional[DatabaseProviderConnectionItemSchema] = None
        self.ingestion: typing.Optional[DatabaseProviderIngestionItemSchema] = None

    @abstractmethod
    def get_databases(self) -> List[DatabaseCreateSchema]:
        """Return all databases in a database provider."""
        pass

    @abstractmethod
    def _get_database_fqn_elements(
        self, provider_name, database_name
    ) -> List[str]:
        """Return the elements of the database fqn."""
        pass

    @abstractmethod
    def get_schemas(
        self, database_name: str
    ) -> List[DatabaseSchemaCreateSchema]:
        """Return all schemas in a database provider."""
        pass

    @abstractmethod
    def _get_schema_fqn_elements(
        self, provider_name, database_name, schema_name
    ) -> List[str]:
        """Return the elements of the schema fqn."""
        pass

    @abstractmethod
    def get_tables(
        self, database_name: str, schema_name: str
    ) -> List[DatabaseTableCreateSchema]:
        """Return all tables in a database provider."""
        pass

    @abstractmethod
    def _get_table_fqn_elements(
        self, provider_name, database_name, schema_name, table_name
    ) -> List[str]:
        """Return the elements of the table fqn."""
        pass

    def supports_schema(self) -> bool:
        """ Indicates if the provider supports the concept of schema """
        return False

    def get_ignorable_schemas(self) -> typing.Set[str]:
        """ Returns the list of schema names to be ignored. In general, they
        are internal schemas.
        """
        return {"information_schema"}
