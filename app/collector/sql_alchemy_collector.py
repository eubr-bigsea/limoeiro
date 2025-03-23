import typing
from abc import abstractmethod
from typing import List

import sqlalchemy as db
from sqlalchemy.engine import create_engine

from app.collector.collector import Collector
from app.schemas import DatabaseTableCreateSchema


class SqlAlchemyCollector(Collector):
    """Class to implement methods, using SqlAlchemy, to collect data in collection engine."""

    def __init__(self, user: str, password: str, host: str, port: str):
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    @abstractmethod
    def get_connection_engine_for_schemas(
        self, database_name: str
    ) -> typing.Optional[db.Engine]:
        """Return the connection engine to get the schemas."""
        pass

    @abstractmethod
    def get_connection_engine_for_tables(
        self, database_name: str, schema_name: str
    ) -> typing.Optional[db.Engine]:
        """Return the connection engine to get the tables."""
        pass

    def get_database_names(self) -> List[str]:
        """Return all databases in a database provider using SqlAlchemy."""
        return self.get_schema_names("")


    def get_tables(
         self, database_name: str, schema_name: str
    ) -> List[DatabaseTableCreateSchema]:
        return []
    #     """Return all tables in a database provider using SqlAlchemy."""
    #     engine = self.get_connection_engine_for_tables(
    #         database_name, schema_name
    #     )
    #     meta_data = db.MetaData()
    #     meta_data.reflect(bind=engine)
    #     engine.dispose()

    #     generic_table_list = []
    #     table_list = meta_data.tables
    #     for table in table_list:
    #         generic_table = GenericTable(table)
    #         for column in table_list[table].columns:
    #             unique = column.unique if column.unique else False
    #             generic_table.add_column(
    #                 GenericColumn(
    #                     column.name,
    #                     column.type,
    #                     column.primary_key,
    #                     column.nullable,
    #                     unique,
    #                 )
    #             )

    #         generic_table_list.append(generic_table)

    #     return generic_table_list

    @abstractmethod
    def _get_connection_string(self) -> str:
        return ""

    @abstractmethod
    def _get_ignorable_dbs(self) -> typing.List[str]:
        return []

    def _get_ignorable_schemas(self) -> typing.List[str]:
        return ["information_schema"]

    @abstractmethod
    def get_databases_names(self) -> List[str]:
        return []

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

    def get_schema_names(self, database_name: typing.Optional[str] = None):
        engine = (
            create_engine(f"{self._get_connection_string()}/{database_name}")
            if database_name
            else create_engine(self._get_connection_string())
        )
        inspector = db.inspect(engine)
        databases = [
            db
            for db in inspector.get_schema_names()
            if db not in self._get_ignorable_dbs()
        ]
        engine.dispose()
        return databases
