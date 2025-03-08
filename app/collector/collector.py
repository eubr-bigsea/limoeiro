
from abc import ABC, abstractmethod

class GenericColumn:
    def __init__(self, name: str, type: str):
        self.name = name
        self.type = type

class GenericTable:
    def __init__(self, name: str):
        self.name = name
        self.columns = []

    def add_column(self, column: GenericColumn):
        self.columns.append(column)


class Collector(ABC):
# Abstract Class to define methods to collect data in collection engine.


    @abstractmethod
    def get_databases(self) -> List[str]:
    # Return all databases in a database provider.
        pass

    @abstractmethod
    def get_schemas(self, database_name) -> List[str]:
    # Return all schemas in a database provider.
        pass

    @abstractmethod
    def get_tables(self, database_name, schema_name) -> List[GenericTable]:
    # Return all tables in a database provider.
        pass

    