import enum
import uuid


DEFAULT_UUID=uuid.UUID('00000000-0000-0000-0000-000000000000')

class DatabaseProviderTypeDisplayName(str, enum.Enum):
    HIVE = "HIVE"
    POSTGRESQL = "POSTGRESQL"
    DRUID = "DRUID"
    ELASTICSEARCH = "ELASTICSEARCH"
    MARIADB = "MARIADB"
    MYSQL = "MYSQL"
    SQLSERVER = "SQLSERVER"

    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls))