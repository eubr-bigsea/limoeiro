from typing import List
from abc import ABC, abstractmethod
import typing

from app.schemas import DatabaseTableCreateSchema


class GenericColumn:
    def __init__(
        self,
        name: str,
        type: str,
        primary_key: bool,
        nullable: bool,
        unique: bool,
    ):
        self.name = name
        self.type = type
        self.primary_key = primary_key
        self.nullable = nullable
        self.unique = unique


class GenericTable:
    def __init__(self, name: str):
        self.name = name
        self.columns = []

    def add_column(self, column: GenericColumn):
        self.columns.append(column)


class Collector(ABC):
    """Abstract Class to define methods to collect data in collection engine."""

    @abstractmethod
    def get_database_names(self) -> List[str]:
        """Return all databases in a database provider."""
        pass

    @abstractmethod
    def _get_database_fqn_elements(
        self, provider_name, database_name
    ) -> List[str]:
        """Return the elements of the database fqn."""
        pass

    @abstractmethod
    def get_schema_names(self, database_name: str) -> List[str]:
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
        return False

    def get_ignorable_schemas(self) -> typing.Set[str]:
        return {"information_schema"}
