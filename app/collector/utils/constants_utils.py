from token import NUMBER


ASSET_ROUTE = "assets"
DOMAIN_ROUTE = "domains"
LAYER_ROUTE = "layers"
PROVIDER_ROUTE = "database-providers"
DATABASE_ROUTE = "databases"
SCHEMA_ROUTE = "schemas"
TABLE_ROUTE = "tables"
CONNECTION_ROUTE = "connections"
INGESTION_ROUTE = "ingestions"
EXECUTION_ROUTE = "executions"

SQLTYPES_DICT = {
    "VARBINARY": "BINARY",
    "DATE": "DATE",
    "BIG_INTEGER": "BIGINT",
    "BIGINTEGER": "BIGINT",
    "LONG": "BIGINT",
    "BLOB": "BLOB",
    "CHAR": "CHAR",
    "DECIMAL": "DECIMAL",
    "ARRAY": "ARRAY",
    "BIGINT": "BIGINT",
    "STRING": "STRING",
    "REAL": "FLOAT",
    "DATETIME": "DATETIME",
    "VARCHAR": "VARCHAR",
    "TIMESTAMP": "TIMESTAMP",
    "NULL": "NULL",
    "JSON": "JSON",
    "JSONB": "JSON",
    "BINARY": "BINARY",
    "ENUM": "ENUM",
    "INTEGER": "INT",
    "BOOLEAN": "BOOLEAN",
    "SMALLINT": "SMALLINT",
    "NUMERIC": "NUMERIC",
    "SMALL_INTEGER": "SMALLINT",
    "TIME": "TIME",
    "CLOB": "CLOB",
    "FLOAT": "FLOAT",
    "TEXT": "TEXT",
    "TINYINT": "TINYINT",
    "LARGE_BINARY": "BINARY",
    "LONGTEXT": "TEXT",
    "TINYTEXT": "TEXT",
    "NVARCHAR": "NVARCHAR",
    "NCHAR": "NCHAR",
    "NTEXT": "NTEXT",
    "MONEY": "MONEY",
    "BIT": "BIT",
    "IMAGE": "IMAGE",

    #Oracle
    "NUMBER": "NUMBER",
    "COMPLETION": "TEXT",
    
    "STR": "STRING",
    "INT": "INT",
    "DICT":"TABLE",
    "LIST":"TABLE",
    "BOOL": "BOOLEAN",
    "NONETYPE": "UNKNOWN",
    "NONE": "UNKNOWN",
}
