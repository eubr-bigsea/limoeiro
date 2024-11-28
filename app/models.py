
import datetime
import enum
import uuid
from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, \
    Enum, DateTime
from sqlalchemy.types import UUID
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

def utc_now() -> datetime.datetime:
    """ Utility function to get current date as UTC"""
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

class TableConstraintType(str, enum.Enum):
    UNIQUE = "UNIQUE"
    PRIMARY_KEY = "PRIMARY_KEY"
    FOREIGN_KEY = "FOREIGN_KEY"
    SORT_KEY = "SORT_KEY"
    DIST_KEY = "DIST_KEY"

    @staticmethod
    def values():
        return [item.value for item in TableConstraintType]
class TableType(str, enum.Enum):
    REGULAR = "REGULAR"
    EXTERNAL = "EXTERNAL"
    VIEW = "VIEW"
    SECURE_VIEW = "SECURE_VIEW"
    MATERIALIZED_VIEW = "MATERIALIZED_VIEW"
    ICEBERG = "ICEBERG"
    LOCAL = "LOCAL"
    PARTITIONED = "PARTITIONED"
    FOREIGN = "FOREIGN"
    TRANSIENT = "TRANSIENT"

    @staticmethod
    def values():
        return [item.value for item in TableType]
class DataType(str, enum.Enum):
    AGGREGATEFUNCTION = "AGGREGATEFUNCTION"
    ARRAY = "ARRAY"
    BIGINT = "BIGINT"
    BINARY = "BINARY"
    BLOB = "BLOB"
    BOOLEAN = "BOOLEAN"
    BYTEA = "BYTEA"
    BYTEINT = "BYTEINT"
    BYTES = "BYTES"
    CHAR = "CHAR"
    CIDR = "CIDR"
    CLOB = "CLOB"
    DATE = "DATE"
    DATETIME = "DATETIME"
    DATETIMERANGE = "DATETIMERANGE"
    DECIMAL = "DECIMAL"
    DOUBLE = "DOUBLE"
    ENUM = "ENUM"
    ERROR = "ERROR"
    FIXED = "FIXED"
    FLOAT = "FLOAT"
    GEOGRAPHY = "GEOGRAPHY"
    GEOMETRY = "GEOMETRY"
    HLLSKETCH = "HLLSKETCH"
    IMAGE = "IMAGE"
    INET = "INET"
    INT = "INT"
    INTERVAL = "INTERVAL"
    IPV4 = "IPV4"
    IPV6 = "IPV6"
    JSON = "JSON"
    LONG = "LONG"
    LONGBLOB = "LONGBLOB"
    LOWCARDINALITY = "LOWCARDINALITY"
    MACADDR = "MACADDR"
    MAP = "MAP"
    MEDIUMBLOB = "MEDIUMBLOB"
    MEDIUMTEXT = "MEDIUMTEXT"
    NTEXT = "NTEXT"
    NULL = "NULL"
    NUMBER = "NUMBER"
    NUMERIC = "NUMERIC"
    PG_LSN = "PG_LSN"
    PG_SNAPSHOT = "PG_SNAPSHOT"
    POINT = "POINT"
    POLYGON = "POLYGON"
    RECORD = "RECORD"
    ROWID = "ROWID"
    SET = "SET"
    SMALLINT = "SMALLINT"
    SPATIAL = "SPATIAL"
    STRING = "STRING"
    STRUCT = "STRUCT"
    SUPER = "SUPER"
    TABLE = "TABLE"
    TEXT = "TEXT"
    TIME = "TIME"
    TIMESTAMP = "TIMESTAMP"
    TIMESTAMPZ = "TIMESTAMPZ"
    TINYINT = "TINYINT"
    TSQUERY = "TSQUERY"
    TSVECTOR = "TSVECTOR"
    TUPLE = "TUPLE"
    TXID_SNAPSHOT = "TXID_SNAPSHOT"
    UNION = "UNION"
    UNKNOWN = "UNKNOWN"
    UUID = "UUID"
    VARBINARY = "VARBINARY"
    VARCHAR = "VARCHAR"
    VARIANT = "VARIANT"
    XML = "XML"
    YEAR = "YEAR"

    @staticmethod
    def values():
        return [item.value for item in DataType]

# Model classes


class Domain(Base):
    """ Um domínio é um contexto delimitado que está alinhado com uma Unidade de Negócios ou uma função dentro de uma organização. """
    __tablename__ = 'tb_domain'
    __table_args__ = (
        UniqueConstraint('fully_qualified_name'),
    )

    # Fields
    id = Column(UUID(as_uuid=True), primary_key=True,
                autoincrement=False,
                default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    display_name = Column(String(200), nullable=False)
    fully_qualified_name = Column(String(500), nullable=False, index=True, unique=True)
    description = Column(String(8000))
    version = Column(String(200),
            default="0.0.0", nullable=False)
    updated_at = Column(DateTime,
            default=utc_now,
            onupdate=utc_now)
    updated_by = Column(String(200), nullable=False)
    href = Column(String(2000))
    owner = Column(String(200))

    # Associations
    database_providers = relationship("DatabaseProvider", back_populates="domain", 
                                      passive_deletes=True, 
                                      lazy="dynamic")

    def __str__(self):
        return self.display_name

    def __repr__(self):
        return f'<Instance {self.__class__}: {self.id}>'


class DatabaseProviderType(Base):
    """ Tipo de provedor de banco de dados """
    __tablename__ = 'tb_database_provider_type'

    # Fields
    id = Column(String(200), primary_key=True,
                autoincrement=False,
                )
    display_name = Column(String(200), nullable=False)
    image = Column(String(8000))

    def __str__(self):
        return self.display_name

    def __repr__(self):
        return f'<Instance {self.__class__}: {self.id}>'


class DatabaseProvider(Base):
    """ Provedor de banco de dados """
    __tablename__ = 'tb_database_provider'
    __table_args__ = (
        UniqueConstraint('fully_qualified_name'),
    )

    # Fields
    id = Column(UUID(as_uuid=True), primary_key=True,
                autoincrement=False,
                default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    fully_qualified_name = Column(String(500), nullable=False, index=True, unique=True)
    display_name = Column(String(200), nullable=False)
    description = Column(String(8000))
    version = Column(String(200),
            default="0.0.0", nullable=False)
    updated_at = Column(DateTime,
            default=utc_now,
            onupdate=utc_now)
    updated_by = Column(String(200), nullable=False)
    owner = Column(String(200))
    href = Column(String(2000))
    deleted = Column(Boolean,
            default=False, nullable=False)
    configuration = Column(JSON)

    # Associations
    provider_type_id = Column(
       String(200),
        ForeignKey("tb_database_provider_type.id",
        name="fk_database_provider_provider_type_id"),
                               nullable=False,
                           index=True)
    provider_type = relationship(
        "DatabaseProviderType",
            #overlaps='database_providers',
            single_parent=True,
            foreign_keys=[provider_type_id], lazy='joined')
    domain_id = Column(
       UUID(as_uuid=True),
        ForeignKey("tb_domain.id",
        name="fk_database_provider_domain_id", ondelete="set null"),
                           index=True)
    domain = relationship(
        "Domain",
            #overlaps='database_providers',
            single_parent=True,
            foreign_keys=[domain_id],
    back_populates="database_providers", lazy='joined')

    def __str__(self):
        return self.display_name

    def __repr__(self):
        return f'<Instance {self.__class__}: {self.id}>'


class Database(Base):
    """ Banco de dados """
    __tablename__ = 'tb_database'
    __table_args__ = (
        UniqueConstraint('fully_qualified_name'),
    )

    # Fields
    id = Column(UUID(as_uuid=True), primary_key=True,
                autoincrement=False,
                default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    fully_qualified_name = Column(String(500), nullable=False, index=True, unique=True)
    display_name = Column(String(200), nullable=False)
    description = Column(String(8000))
    version = Column(String(200),
            default="0.0.0", nullable=False)
    updated_at = Column(DateTime,
            default=utc_now,
            onupdate=utc_now)
    updated_by = Column(String(200), nullable=False)
    owner = Column(String(200))
    href = Column(String(2000))
    deleted = Column(Boolean,
            default=False, nullable=False)
    retention_period = Column(String(100))

    # Associations
    provider_id = Column(
       UUID(as_uuid=True),
        ForeignKey("tb_database_provider.id",
        name="fk_database_provider_id"),
                               nullable=False,
                           index=True)
    provider = relationship(
        "DatabaseProvider",
            #overlaps='database',
            single_parent=True,
            foreign_keys=[provider_id], lazy='joined')
    domain_id = Column(
       UUID(as_uuid=True),
        ForeignKey("tb_domain.id",
        name="fk_database_domain_id"),
                           index=True)
    domain = relationship(
        "Domain",
            #overlaps='database',
            single_parent=True,
            foreign_keys=[domain_id], lazy='joined')

    def __str__(self):
        return self.display_name

    def __repr__(self):
        return f'<Instance {self.__class__}: {self.id}>'


class DatabaseSchema(Base):
    """ Esquema """
    __tablename__ = 'tb_database_schema'
    __table_args__ = (
        UniqueConstraint('fully_qualified_name'),
    )

    # Fields
    id = Column(UUID(as_uuid=True), primary_key=True,
                autoincrement=False,
                default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    display_name = Column(String(200), nullable=False)
    fully_qualified_name = Column(String(500), nullable=False, index=True, unique=True)
    description = Column(String(8000))
    version = Column(String(200),
            default="0.0.0", nullable=False)
    updated_at = Column(DateTime,
            default=utc_now,
            onupdate=utc_now)
    updated_by = Column(String(200), nullable=False)
    href = Column(String(2000))
    owner = Column(String(200))
    deleted = Column(Boolean,
            default=False, nullable=False)

    # Associations
    database_id = Column(
       UUID(as_uuid=True),
        ForeignKey("tb_database.id",
        name="fk_database_schema_database_id"),
                               nullable=False,
                           index=True)
    database = relationship(
        "Database",
            #overlaps='schema',
            single_parent=True,
            foreign_keys=[database_id], lazy='joined')

    def __str__(self):
        return self.display_name

    def __repr__(self):
        return f'<Instance {self.__class__}: {self.id}>'


class DatabaseTable(Base):
    """ Tabela """
    __tablename__ = 'tb_database_table'
    __table_args__ = (
        UniqueConstraint('fully_qualified_name'),
    )

    # Fields
    id = Column(UUID(as_uuid=True), primary_key=True,
                autoincrement=False,
                default=uuid.uuid4)
    type = Column(Enum(TableType,
                       name='TableTypeEnumType'), nullable=False)
    name = Column(String(200), nullable=False)
    display_name = Column(String(200), nullable=False)
    fully_qualified_name = Column(String(500), nullable=False, index=True, unique=True)
    description = Column(String(8000))
    version = Column(String(200),
            default="0.0.0", nullable=False)
    updated_at = Column(DateTime,
            default=utc_now,
            onupdate=utc_now)
    updated_by = Column(String(200), nullable=False)
    href = Column(String(2000))
    owner = Column(String(200))
    deleted = Column(Boolean,
            default=False, nullable=False)
    proxy_enabled = Column(Boolean,
            default=False, nullable=False)
    query = Column(String(8000))
    cache_type = Column(String(200))
    cache_ttl_in_seconds = Column(Integer)
    cache_validation = Column(String(8000))

    # Associations
    database_id = Column(
       UUID(as_uuid=True),
        ForeignKey("tb_database.id",
        name="fk_database_table_database_id"),
                               nullable=False,
                           index=True)
    database = relationship(
        "Database",
            #overlaps='schema',
            single_parent=True,
            foreign_keys=[database_id], lazy='joined')
    database_schema_id = Column(
       UUID(as_uuid=True),
        ForeignKey("tb_database_schema.id",
        name="fk_database_table_database_schema_id"),
                               nullable=False,
                           index=True)
    database_schema = relationship(
        "DatabaseSchema",
            #overlaps='schema',
            single_parent=True,
            foreign_keys=[database_schema_id], lazy='joined')
    columns = relationship("TableColumn", 
                           lazy="joined")

    def __str__(self):
        return self.display_name

    def __repr__(self):
        return f'<Instance {self.__class__}: {self.id}>'


class TableConstraint(Base):
    """ Restrição de tabela """
    __tablename__ = 'tb_table_constraint'

    # Fields
    id = Column(UUID(as_uuid=True), primary_key=True,
                autoincrement=False,
                default=uuid.uuid4)
    type = Column(Enum(TableConstraintType,
                       name='TableConstraintTypeEnumType'), nullable=False)

    # Associations
    table_id = Column(
       UUID(as_uuid=True),
        ForeignKey("tb_database_table.id",
        name="fk_table_constraint_table_id"),
                               nullable=False,
                           index=True)
    table = relationship(
        "DatabaseTable",
            #overlaps='table_constraint',
            single_parent=True,
            foreign_keys=[table_id])

    def __str__(self):
        return ""

    def __repr__(self):
        return f'<Instance {self.__class__}: {self.id}>'


class TableProfile(Base):
    """ Perfil de tabela """
    __tablename__ = 'tb_table_profile'

    # Fields
    id = Column(UUID(as_uuid=True), primary_key=True,
                autoincrement=False,
                default=uuid.uuid4)
    updated_at = Column(DateTime)
    table_created_at = Column(DateTime)
    column_count = Column(Integer)
    row_count = Column(Integer)
    size_in_bytes = Column(Integer)

    # Associations
    table_id = Column(
       UUID(as_uuid=True),
        ForeignKey("tb_database_table.id",
        name="fk_table_profile_table_id"),
                               nullable=False,
                           index=True)
    table = relationship(
        "DatabaseTable",
            #overlaps='table_profile',
            single_parent=True,
            foreign_keys=[table_id])

    def __str__(self):
        return ""

    def __repr__(self):
        return f'<Instance {self.__class__}: {self.id}>'


class TableColumn(Base):
    """ Coluna """
    __tablename__ = 'tb_table_column'

    # Fields
    id = Column(UUID(as_uuid=True), primary_key=True,
                autoincrement=False,
                default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(String(8000))
    data_type = Column(Enum(DataType,
                            name='DataTypeEnumType'), nullable=False)
    array_data_type = Column(String(200))
    size = Column(Integer)
    precision = Column(Integer)
    scale = Column(Integer)
    position = Column(Integer)
    primary_key = Column(Boolean,
            default=False, nullable=False)
    nullable = Column(Boolean,
            default=True, nullable=False)
    unique = Column(Boolean,
            default=False, nullable=False)

    # Associations
    table_id = Column(
       UUID(as_uuid=True),
        ForeignKey("tb_database_table.id",
        name="fk_table_column_table_id"),
                               nullable=False,
                           index=True)

    def __str__(self):
        return self.display_name

    def __repr__(self):
        return f'<Instance {self.__class__}: {self.id}>'


class ColumnProfile(Base):
    """ Perfil de Coluna """
    __tablename__ = 'tb_column_profile'

    # Fields
    id = Column(UUID(as_uuid=True), primary_key=True,
                autoincrement=False,
                default=uuid.uuid4)
    updated_at = Column(DateTime)
    values_count = Column(Integer)
    values_percentage = Column(Float)
    valid_count = Column(Integer)
    duplicate_count = Column(Integer)
    null_count = Column(Integer)
    null_proportion = Column(Float)
    missing_percentage = Column(Float)
    missing_count = Column(Integer)
    unique_count = Column(Integer)
    unique_proportion = Column(Float)
    distinct_count = Column(Integer)
    distinct_proportion = Column(Float)
    min = Column(String(200))
    max = Column(String(200))
    min_length = Column(Integer)
    max_length = Column(Integer)
    mean = Column(Float)
    sum = Column(Float)
    stddev = Column(Float)
    variance = Column(Float)
    median = Column(Float)
    first_quartile = Column(Float)
    third_quartile = Column(Float)
    inter_quartile_range = Column(Float)
    non_parametric_skew = Column(Float)
    histogram = Column(JSON)

    # Associations
    column_id = Column(
       UUID(as_uuid=True),
        ForeignKey("tb_table_column.id",
        name="fk_column_profile_column_id"),
                               nullable=False,
                           index=True)
    column = relationship(
        "TableColumn",
            #overlaps='profile',
            single_parent=True,
            foreign_keys=[column_id])
    table_id = Column(
       UUID(as_uuid=True),
        ForeignKey("tb_database_table.id",
        name="fk_column_profile_table_id"),
                               nullable=False,
                           index=True)
    table = relationship(
        "DatabaseTable",
            #overlaps='profile',
            single_parent=True,
            foreign_keys=[table_id])

    def __str__(self):
        return ""

    def __repr__(self):
        return f'<Instance {self.__class__}: {self.id}>'


class Role(Base):
    """ Perfil de usuário """
    __tablename__ = 'tb_role'

    # Fields
    id = Column(UUID(as_uuid=True), primary_key=True,
                autoincrement=False,
                default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    deleted = Column(Boolean,
            default=False, nullable=False)

    def __str__(self):
        return ""

    def __repr__(self):
        return f'<Instance {self.__class__}: {self.id}>'


class Action(Base):
    """ Ação associada aos objetos """
    __tablename__ = 'tb_action'

    # Fields
    id = Column(UUID(as_uuid=True), primary_key=True,
                autoincrement=False,
                default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    deleted = Column(Boolean,
            default=False, nullable=False)
    applies_to = Column(String(200), nullable=False)

    def __str__(self):
        return ""

    def __repr__(self):
        return f'<Instance {self.__class__}: {self.id}>'


class TableRole(Base):
    """ Associação entre as entidades Table, Role e Action """
    __tablename__ = 'tb_table_role'

    # Fields
    id = Column(Integer, primary_key=True)
    parameters = Column(JSON)

    # Associations
    table_id = Column(
       UUID(as_uuid=True),
        ForeignKey("tb_database_table.id",
        name="fk_table_role_table_id"),
                               nullable=False,
                           index=True)
    table = relationship(
        "DatabaseTable",
            #overlaps='table_role_action',
            single_parent=True,
            foreign_keys=[table_id])
    role_id = Column(
       UUID(as_uuid=True),
        ForeignKey("tb_role.id",
        name="fk_table_role_role_id"),
                               nullable=False,
                           index=True)
    role = relationship(
        "Role",
            #overlaps='table_role_action',
            single_parent=True,
            foreign_keys=[role_id])
    action_id = Column(
       UUID(as_uuid=True),
        ForeignKey("tb_action.id",
        name="fk_table_role_action_id"),
                               nullable=False,
                           index=True)
    action = relationship(
        "Action",
            #overlaps='table_role_action',
            single_parent=True,
            foreign_keys=[action_id])

    def __str__(self):
        return ""

    def __repr__(self):
        return f'<Instance {self.__class__}: {self.id}>'
