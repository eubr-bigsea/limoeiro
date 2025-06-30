import logging
import typing
from typing import List, Optional
from sqlalchemy.engine import create_engine
import sqlalchemy as db
from sqlalchemy import ARRAY
from app.collector.sql_alchemy_collector import SqlAlchemyCollector
from app.collector import DEFAULT_UUID
from app.schemas import (
    DatabaseCreateSchema,
    DatabaseTableCreateSchema,
    TableColumnCreateSchema
)
from app.collector.utils.constants_utils import SQLTYPES_DICT
from app.models import DataType
import sqlalchemy
from app.models import DataType, TableType
logger = logging.getLogger(__name__)




class HiveCollector(SqlAlchemyCollector):
    """Class to implement methods, to collect data in HIVE."""

    def _get_connection_string(self):
        params = self.connection_info
        if params is not None:
            return f"hive://{params.user_name}:{params.password}@{params.host}:{params.port}"
        return "FIXME"

    def get_connection_engine_for_tables(
        self, database_name: str, schema_name: str
    ):
        """Return the connection engine to get the tables."""
        engine = create_engine(self._get_connection_string()+f"/{schema_name}",
                               connect_args={'auth': 'LDAP'})
        return engine

    def get_view_names(self, schema_name: str,
                      engine, inspector) -> List[str]:
        """Return the views names."""

        view_names = []
        query = db.text("SHOW TABLES")
        with engine.connect() as conn:
            result = conn.execute(query)
            tables = result.fetchall()

            for table in tables:
                table_name = table[0]
                describe_query = db.text(f"DESCRIBE FORMATTED {table_name}")

                desc_result = conn.execute(describe_query)
                describe = desc_result.fetchall()

                if any("VIRTUAL_VIEW" in str(row) for row in describe):
                    view_names.append(table_name)
        return view_names

    def get_databases(self) -> List[DatabaseCreateSchema]:
        """Return all databases."""
        engine = create_engine(self._get_connection_string(), connect_args={'auth': 'LDAP'})
        insp = db.inspect(engine)
        result = insp.get_schema_names()
        engine.dispose()

        return [
            DatabaseCreateSchema(
                name=r,
                display_name=r,
                fully_qualified_name="placeholder",
                provider_id=DEFAULT_UUID,
            )
            for r in result
        ]
        
    def get_tables(
        self, database_name: str, schema_name: str
    ) -> List[DatabaseTableCreateSchema]:
        engine = self.get_connection_engine_for_tables(
            database_name, schema_name
        )
       
        inspector = sqlalchemy.inspect(engine)
        tables = []
        if self.supports_views():
            view_names = self.get_view_names(schema_name, engine, inspector)
        else:
            view_names = []
            logger.info("Provedor de dados não suporta views")
        table_names = inspector.get_table_names(schema=schema_name)
        for item_type, items in zip(
            ["VIEW", "REGULAR"], [view_names, table_names]
        ):
            for name in items:
                columns: typing.List[TableColumnCreateSchema] = []
                if self.supports_pk():
                    primary_keys = inspector.get_pk_constraint(
                        name, schema=schema_name
                    ).get("constrained_columns", [])
                else:
                    primary_keys = []
                try:
                    unique_constraints = inspector.get_unique_constraints(
                        name, schema=schema_name
                    )
                except NotImplementedError:
                    logger.info(
                        "Provedor de dados não suporta unique constraint"
                    )
                    unique_constraints = []

                unique_columns = [
                    col
                    for constraint in unique_constraints
                    for col in constraint.get("column_names", [])
                    if len(constraint.get("column_names", [])) == 1
                ]
                
                query = db.text(f"DESCRIBE FORMATTED {name}")
                with engine.connect() as conn:
                    result = conn.execute(query).fetchall()

                for i, column in enumerate(
                    inspector.get_columns(name, schema=schema_name)
                ):
                    column["table_name"] = name
                    column["schema_name"] = schema_name
                    
                    data_type, array_data_type = self.get_data_type_str(column)
                    
                    columns.append(
                        TableColumnCreateSchema(
                            name=column.get("name"),
                            description= self.get_column_comment(result, column.get("name")),
                            # FIXME: add notes
                            display_name=column.get("name"),
                            data_type=data_type,
                            array_data_type=array_data_type,
                            size=getattr(column.get("type"), "length", None),
                            precision=getattr(
                                column.get("type"), "precision", None
                            ),
                            scale=getattr(column.get("type"), "scale", None),
                            nullable=column.get("nullable"),
                            position=i,
                            primary_key=column.get("name") in primary_keys,
                            unique=column.get("name") in unique_columns,
                            default_value=column.get("default"),
                        )
                    )
                   
                table_comment = self.get_table_comment(result) 
                
                if self.supports_schema():
                    table_fqn = f"{database_name}.{schema_name}.{name}"
                else:
                    table_fqn = f"{database_name}.{name}"

                database_table = self.post_process_table(
                    engine,
                    DatabaseTableCreateSchema(
                        name=name,
                        display_name=name,
                        fully_qualified_name=table_fqn,
                        notes=table_comment,
                        database_id=DEFAULT_UUID,
                        columns=columns,
                        type=TableType[item_type],
                    ),
                )
                tables.append(database_table)
        engine.dispose()

        return tables
        
    def get_table_comment(self, result) -> str:
        """Return the table comment."""
        try:
            in_table_parameters = False

            for row in result:
                
                if row[0] == 'Table Parameters:':
                    in_table_parameters = True
                    continue 

                if in_table_parameters and row[1] and row[1].strip().lower() == "comment":
                    return row[2].strip()

                if row[0].startswith('#') and row[0] != '# Table Parameters:':
                    in_table_parameters = False
                    
            return None
        except Exception as e:
            return None
        
        
    import sqlalchemy as db

    def get_column_comment(self, result, name) -> str:
        """Return the column comment."""
        try:
            in_columns_section = False
            for row in result:
                if row[0] and row[0].strip().lower() == "# col_name":
                    in_columns_section = True
                    continue
                
                if in_columns_section:
                    col_name_from_desc = row[0].strip() if row[0] is not None else ""
                    if not col_name_from_desc and row[1] is None and row[2] is None:
                        break
                    if col_name_from_desc == name:
                        return (row[2] or "").strip() 

            return None
        except Exception as e:
            return None

    def supports_schema(self):
        return False

    def get_connection_engine_for_schemas(
        self, database_name: str
    ) -> Optional[db.Engine]:
        """Return the connection engine to get the schemas."""
        return None

    def _get_ignorable_dbs(self) -> List[str]:
        return []

    def supports_pk(self) -> bool:
        """Return if the database supports primary keys."""
        return False

    def get_data_type_str(self, column) -> str:
        """Return the data type from a column."""
        data_type_str = SQLTYPES_DICT[str(column.get("type"))]
        return data_type_str
    
    
    def get_data_type_str(self, column) -> str:
        """Return the data type from a column."""
        column_type = column.get("type")
        
        data_type = SQLTYPES_DICT[
            str(column_type)
        ]
        data_type=DataType[data_type]
        
        array_data_type = None
        if isinstance(column_type, ARRAY):
            array_data_type = SQLTYPES_DICT[
                str(column.get("type").get("item_type"))
            ]
            array_data_type=DataType[array_data_type]
        
        return data_type, array_data_type
    
    

