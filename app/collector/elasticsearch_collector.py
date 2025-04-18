from typing import List

GenericTable = str

from app.collector.collector import Collector

from elasticsearch import Elasticsearch


class ElasticsearchCollector(Collector):
    """Class to implement methods, to collect data in Elasticsearch."""

    def __init__(self):
        super().__init__()

    def get_tables(
        self, database_name: str, schema_name: str
    ) -> List[GenericTable]:
        """Return all tables in a database provider."""

        es = Elasticsearch(
            self.host,
            port=self.port,
            http_auth=(self.user, self.password),
            http_compress=True,
        )

        dict_es = es.indices.get("*")
        dict_es_keys = dict_es.keys()

        tables = []
        for idx in dict_es_keys:
            if "properties" in  dict_es[idx]["mappings"]:
                idx_fields = dict_es[idx]["mappings"]["properties"]

                columns: typing.List[TableColumnCreateSchema] = []
                for field in idx_fields.keys():
                    columns.append(
                            TableColumnCreateSchema(
                                name=field,
                                display_name=field,
                                data_type=DataType[idx_fields[field]["type"]]
                            )
                    )
                name = idx
                database_table = DatabaseTableCreateSchema(
                            name=name,
                            display_name=name,
                            fully_qualified_name=f"{database_name}.{name}",
                            database_id=DEFAULT_UUID,
                            columns=columns,
                            type=TableType.REGULAR.value
                        )
                tables.append(database_table)

        es.close()

        return tables

    def get_databases(self) -> typing.List[DatabaseCreateSchema]:
        """Return all databases."""
        
        return [
            DatabaseCreateSchema(
                name="default",
                display_name="default",
                fully_qualified_name="placeholder",
                provider_id=DEFAULT_UUID,
            )
        ]

    def supports_schema(self):
        return False
