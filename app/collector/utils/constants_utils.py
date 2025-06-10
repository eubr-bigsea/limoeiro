from token import NUMBER


ASSET_ROUTE = "assets"
DOMAIN_ROUTE = "domains"
LAYER_ROUTE = "layers"
PROVIDER_ROUTE = "database-providers"
DATABASE_ROUTE = "databases"
SAMPLE_ROUTE = "samples"
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
    "HALF_FLOAT": "FLOAT",
    "TEXT": "TEXT",
    "TINYINT": "TINYINT",
    "LARGE_BINARY": "BINARY",
    "LONGTEXT": "TEXT",
    "TINYTEXT": "TEXT",
    "KEYWORD": "TEXT",
    "NVARCHAR": "NVARCHAR",
    "NCHAR": "NCHAR",
    "NTEXT": "NTEXT",
    "MONEY": "MONEY",
    "BIT": "BIT",
    "IMAGE": "IMAGE",
    "NUMBER": "NUMBER",
    "COMPLETION": "TEXT",
    "STR": "STRING",
    "INT": "INT",
    "DICT":"JSON",
    "OBJECT":"JSON",
    "LIST":"ARRAY",
    "NESTED": "ARRAY",
    "BOOL": "BOOLEAN",
    "NONETYPE": "UNKNOWN",
    "NONE": "UNKNOWN",
    "DOUBLE": "DOUBLE",
    "DATE_RANGE": "TUPLE",
    "DOUBLE_RANGE": "TUPLE",
    "FLOAT_RANGE": "TUPLE",
    "INTEGER_RANGE": "TUPLE",
    "IP_RANGE": "TUPLE",
    "LONG_RANGE": "TUPLE",
    "BYTE": "BYTES",
    "DATE_NANOS": "DATETIME",
    "SEARCH_AS_YOU_TYPE": "TEXT",
    "SHORT": "INT",
    "SHAPE": "GEOMETRY",
    "ALIAS": "UNKNOWN",
    "GEO_POINT": "GEOGRAPHY",
    "GEO_SHAPE": "GEOGRAPHY",
    "FLATTENED": "JSON",
    "DENSE_VECTOR": "ARRAY",
    "IP": "IPV4",
    "CONSTANT_KEYWORD": "TEXT",
    
}
