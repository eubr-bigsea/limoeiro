import datetime
import enum
import uuid
from .database import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy import (
    Integer,
    String,
    Boolean,
    ForeignKey,
    Float,
    Enum,
    DateTime,
    Text,
)
from sqlalchemy.types import UUID
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint


def utc_now() -> datetime.datetime:
    """Utility function to get current date as UTC"""
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


class LinkType(str, enum.Enum):
    DOCUMENTATION = "DOCUMENTATION"
    SOURCE_CODE = "SOURCE_CODE"
    DEPLOYMENT = "DEPLOYMENT"
    OTHER = "OTHER"

    @staticmethod
    def values():
        return [item.value for item in LinkType]


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


class DatabaseProviderTypeDisplayName(str, enum.Enum):
    HIVE = "HIVE"
    POSTGRES = "POSTGRES"
    DRUID = "DRUID"       
    ELASTICSEARCH = "ELASTICSEARCH"

    @staticmethod
    def values():
        return [item.value for item in DatabaseProviderType]

# Model classes


class User(Base):
    """Usuário"""

    __tablename__ = "tb_user"
    __table_args__ = (UniqueConstraint("login", name="inx_uq_user"),)

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    name = mapped_column(String(200), nullable=False)
    deleted = mapped_column(
        Boolean, default=False, nullable=False, server_default="False"
    )
    login = mapped_column(String(200), nullable=False)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class ResponsibilityType(Base):
    """Tipo de responsabilidade"""

    __tablename__ = "tb_responsibility_type"
    __table_args__ = (
        UniqueConstraint("name", name="inx_uq_responsibility_type"),
    )

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    name = mapped_column(String(200), nullable=False)
    description = mapped_column(String(8000))
    deleted = mapped_column(
        Boolean, default=False, nullable=False, server_default="False"
    )

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class AssetLink(Base):
    """Link (url) para um ativo."""

    __tablename__ = "tb_asset_link"

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    url = mapped_column(String(2000))
    type = mapped_column(Enum(LinkType, name="LinkTypeEnumType"), nullable=False)

    # Associations
    asset_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_asset.id", name="fk_asset_link_asset_id"),
        nullable=False,
        index=True,
    )
    asset = relationship("Asset", foreign_keys=[asset_id])

    def __str__(self):
        return str("")

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class Layer(Base):
    """Camada lógica para organização dos dados"""

    __tablename__ = "tb_layer"
    __table_args__ = (UniqueConstraint("name", name="inx_uq_layer"),)

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    name = mapped_column(String(200), nullable=False)
    description = mapped_column(String(8000))
    deleted = mapped_column(
        Boolean, default=False, nullable=False, server_default="False"
    )

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class Domain(Base):
    """Um domínio é um contexto delimitado que está alinhado com uma Unidade de Negócios ou uma função dentro de uma organização."""

    __tablename__ = "tb_domain"
    __table_args__ = (UniqueConstraint("name", name="inx_uq_domain"),)

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    name = mapped_column(String(200), nullable=False)
    description = mapped_column(String(8000))
    deleted = mapped_column(
        Boolean, default=False, nullable=False, server_default="False"
    )

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class DatabaseProviderType(Base):
    """Tipo de provedor de banco de dados"""

    __tablename__ = "tb_database_provider_type"

    # Fields
    id = mapped_column(
        String(200),
        primary_key=True,
        autoincrement=False,
    )
    display_name = mapped_column(String(200), nullable=False)
    image = mapped_column(String(8000))

    def __str__(self):
        return str(self.display_name)

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class Tag(Base):
    """Tag"""

    __tablename__ = "tb_tag"
    __table_args__ = (UniqueConstraint("name", name="inx_uq_tag"),)

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    name = mapped_column(String(200), nullable=False)
    deleted = mapped_column(
        Boolean, default=False, nullable=False, server_default="False"
    )
    description = mapped_column(String(8000))
    applicable_to = mapped_column(String(200))

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class EntityTag(Base):
    """Tags associadas às entidades"""

    __tablename__ = "tb_entity_tag"
    __table_args__ = (
        UniqueConstraint("entity_type", "entity_id", name="inx_uq_entity_tag"),
    )

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    entity_type = mapped_column(String(200), nullable=False)
    entity_id = mapped_column(UUID(as_uuid=True), nullable=False)

    # Associations
    tag_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_tag.id", name="fk_entity_tag_tag_id"),
        nullable=False,
        index=True,
    )
    tag = relationship("Tag", foreign_keys=[tag_id])

    def __str__(self):
        return str("")

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class Asset(Base):
    """Ativo no catalogo de dados"""

    __tablename__ = "tb_asset"
    __table_args__ = (
        UniqueConstraint(
            "fully_qualified_name", "asset_type", name="inx_uq_asset"
        ),
    )

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    name = mapped_column(String(200), nullable=False)
    fully_qualified_name = mapped_column(
        String(500), nullable=False, index=True, unique=True
    )
    display_name = mapped_column(String(200), nullable=False)
    description = mapped_column(String(8000))
    notes = mapped_column(String(8000))
    deleted = mapped_column(
        Boolean, default=False, nullable=False, server_default="False"
    )
    version = mapped_column(String(200), default="0.0.0", nullable=False)
    updated_at = mapped_column(DateTime, default=utc_now, onupdate=utc_now)
    updated_by = mapped_column(String(200), nullable=False)
    asset_type = mapped_column(String(20), nullable=False)

    # Associations
    domain_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "tb_domain.id", name="fk_asset_domain_id", ondelete="set null"
        ),
        index=True,
    )
    domain = relationship("Domain", foreign_keys=[domain_id], lazy="joined")

    __mapper_args__ = {
        "polymorphic_identity": "asset",
        "polymorphic_on": asset_type,
    }
    layer_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_layer.id", name="fk_asset_layer_id", ondelete="set null"),
        index=True,
    )
    layer = relationship("Layer", foreign_keys=[layer_id], lazy="joined")

    __mapper_args__ = {
        "polymorphic_identity": "asset",
        "polymorphic_on": asset_type,
    }
    links = relationship("AssetLink", lazy="joined")

    __mapper_args__ = {
        "polymorphic_identity": "asset",
        "polymorphic_on": asset_type,
    }

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class DatabaseProvider(Asset):
    """Provedor de banco de dados"""

    __tablename__ = "tb_database_provider"

    # Fields
    id = mapped_column(
        ForeignKey("tb_asset.id"),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    configuration = mapped_column(JSON)

    # Associations
    provider_type_id = mapped_column(
        String(200),
        ForeignKey(
            "tb_database_provider_type.id",
            name="fk_database_provider_provider_type_id",
        ),
        nullable=False,
        index=True,
    )
    provider_type = relationship(
        "DatabaseProviderType", foreign_keys=[provider_type_id], lazy="joined"
    )

    __mapper_args__ = {
        "polymorphic_identity": "provider",
        "inherit_condition": (id == Asset.id),
    }
    connection_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "tb_database_provider_connection.id",
            name="fk_database_provider_connection_id",
        ),
        index=True,
    )
    connection = relationship(
        "DatabaseProviderConnection", foreign_keys=[connection_id], lazy="raise"
    )

    __mapper_args__ = {
        "polymorphic_identity": "provider",
        "inherit_condition": (id == Asset.id),
    }
    ingestions = relationship("DatabaseProviderIngestion", lazy="joined")

    __mapper_args__ = {
        "polymorphic_identity": "provider",
        "inherit_condition": (id == Asset.id),
    }

    def __str__(self):
        return str("")

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class DatabaseProviderConnection(Base):
    """Conexão ao provedor de banco de dados"""

    __tablename__ = "tb_database_provider_connection"

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    user_name = mapped_column(String(100), nullable=False)
    password = mapped_column(String(100))
    host = mapped_column(String(400), nullable=False)
    port = mapped_column(Integer, nullable=False)
    database = mapped_column(String(200))
    extra_parameters = mapped_column(JSON)

    def __str__(self):
        return str("")

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class DatabaseProviderIngestion(Base):
    """Ingestão de dados associada a um provedor de banco de dados"""

    __tablename__ = "tb_database_provider_ingestion"

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    name = mapped_column(String(200), nullable=False)
    deleted = mapped_column(
        Boolean, default=False, nullable=False, server_default="False"
    )
    type = mapped_column(String(100), nullable=False)
    include_database = mapped_column(String(1000))
    exclude_database = mapped_column(String(1000))
    include_schema = mapped_column(String(1000))
    exclude_schema = mapped_column(String(1000))
    include_table = mapped_column(String(1000))
    exclude_table = mapped_column(String(1000))
    include_view = mapped_column(Boolean, default=False, nullable=False)
    override_mode = mapped_column(String(200))
    scheduling = mapped_column(JSON)
    recent_runs_statuses = mapped_column(String(100))
    retries = mapped_column(Integer, default=5, nullable=False)

    # Associations
    provider_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "tb_database_provider.id",
            name="fk_database_provider_ingestion_provider_id",
        ),
        nullable=False,
        index=True,
    )
    provider = relationship(
        "DatabaseProvider",
        back_populates="ingestions",
        foreign_keys=[provider_id],
    )
    logs = relationship("DatabaseProviderIngestionLog", lazy="joined")

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class DatabaseProviderIngestionLog(Base):
    """Banco de dados"""

    __tablename__ = "tb_database_provider_ingestion_log"

    # Fields
    id = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    updated_at = mapped_column(DateTime, default=utc_now, onupdate=utc_now)
    status = mapped_column(String(100), nullable=False)
    log = mapped_column(Text)

    # Associations
    ingestion_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "tb_database_provider_ingestion.id",
            name="fk_database_provider_ingestion_log_ingestion_id",
        ),
        nullable=False,
        index=True,
    )
    ingestion = relationship(
        "DatabaseProviderIngestion",
        back_populates="logs",
        foreign_keys=[ingestion_id],
    )

    def __str__(self):
        return str("")

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class Database(Asset):
    """Banco de dados"""

    __tablename__ = "tb_database"

    # Fields
    id = mapped_column(
        ForeignKey("tb_asset.id"),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    retention_period = mapped_column(String(100))

    # Associations
    provider_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_database_provider.id", name="fk_database_provider_id"),
        nullable=False,
        index=True,
    )
    provider = relationship(
        "DatabaseProvider", foreign_keys=[provider_id], lazy="joined"
    )

    __mapper_args__ = {
        "polymorphic_identity": "database",
        "inherit_condition": (id == Asset.id),
    }

    def __str__(self):
        return str("")

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class DatabaseSchema(Asset):
    """Esquema"""

    __tablename__ = "tb_database_schema"

    # Fields
    id = mapped_column(
        ForeignKey("tb_asset.id"),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )

    # Associations
    database_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_database.id", name="fk_database_schema_database_id"),
        nullable=False,
        index=True,
    )
    database = relationship(
        "Database", foreign_keys=[database_id], lazy="joined"
    )

    __mapper_args__ = {
        "polymorphic_identity": "schema",
        "inherit_condition": (id == Asset.id),
    }

    def __str__(self):
        return str("DatabaseSchema")

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class DatabaseTable(Asset):
    """Tabela"""

    __tablename__ = "tb_database_table"

    # Fields
    id = mapped_column(
        ForeignKey("tb_asset.id"),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    type = mapped_column(
        Enum(TableType, name="TableTypeEnumType"),
        default="REGULAR",
        nullable=False,
    )
    proxy_enabled = mapped_column(Boolean, default=False, nullable=False)
    query = mapped_column(String(8000))
    cache_type = mapped_column(String(200))
    cache_ttl_in_seconds = mapped_column(Integer)
    cache_validation = mapped_column(String(8000))

    # Associations
    database_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_database.id", name="fk_database_table_database_id"),
        nullable=False,
        index=True,
    )
    database = relationship(
        "Database", foreign_keys=[database_id], lazy="joined"
    )

    __mapper_args__ = {
        "polymorphic_identity": "table",
        "inherit_condition": (id == Asset.id),
    }
    database_schema_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "tb_database_schema.id", name="fk_database_table_database_schema_id"
        ),
        nullable=False,
        index=True,
    )
    database_schema = relationship(
        "DatabaseSchema", foreign_keys=[database_schema_id], lazy="joined"
    )

    __mapper_args__ = {
        "polymorphic_identity": "table",
        "inherit_condition": (id == Asset.id),
    }
    columns = relationship("TableColumn", lazy="joined")

    __mapper_args__ = {
        "polymorphic_identity": "table",
        "inherit_condition": (id == Asset.id),
    }

    def __str__(self):
        return str("")

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class DatabaseTableSample(Base):
    """Amostra de Tabela"""

    __tablename__ = "tb_database_table_sample"

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    date = mapped_column(DateTime, nullable=False)
    content = mapped_column(JSON, nullable=False)
    is_visible = mapped_column(Boolean, default=True, nullable=False)

    # Associations
    database_table_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "tb_database_table.id",
            name="fk_database_table_sample_database_table_id",
        ),
        nullable=False,
        index=True,
    )
    database_table = relationship(
        "DatabaseTable", foreign_keys=[database_table_id], lazy="joined"
    )

    def __str__(self):
        return str("")

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class TableConstraint(Base):
    """Restrição de tabela"""

    __tablename__ = "tb_table_constraint"

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    type = mapped_column(
        Enum(TableConstraintType, name="TableConstraintTypeEnumType"),
        nullable=False,
    )

    # Associations
    table_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_database_table.id", name="fk_table_constraint_table_id"),
        nullable=False,
        index=True,
    )
    table = relationship("DatabaseTable", foreign_keys=[table_id])

    def __str__(self):
        return str("")

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class TableProfile(Base):
    """Perfil de tabela"""

    __tablename__ = "tb_table_profile"

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    updated_at = mapped_column(DateTime)
    table_created_at = mapped_column(DateTime)
    column_count = mapped_column(Integer)
    row_count = mapped_column(Integer)
    size_in_bytes = mapped_column(Integer)

    # Associations
    table_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_database_table.id", name="fk_table_profile_table_id"),
        nullable=False,
        index=True,
    )
    table = relationship("DatabaseTable", foreign_keys=[table_id])

    def __str__(self):
        return str("")

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class TableColumn(Base):
    """Coluna"""

    __tablename__ = "tb_table_column"

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    name = mapped_column(String(200), nullable=False)
    display_name = mapped_column(String(200), nullable=False)
    description = mapped_column(String(8000))
    data_type = mapped_column(
        Enum(DataType, name="DataTypeEnumType"), nullable=False
    )
    array_data_type = mapped_column(String(200))
    size = mapped_column(Integer)
    precision = mapped_column(Integer)
    scale = mapped_column(Integer)
    position = mapped_column(Integer)
    primary_key = mapped_column(Boolean, default=False, nullable=False)
    nullable = mapped_column(Boolean, default=True, nullable=False)
    unique = mapped_column(Boolean, default=False, nullable=False)
    is_metadata = mapped_column(
        Boolean, default=False, nullable=False, server_default="False"
    )

    # Associations
    table_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_database_table.id", name="fk_table_column_table_id"),
        nullable=False,
        index=True,
    )

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class ColumnProfile(Base):
    """Perfil de Coluna"""

    __tablename__ = "tb_column_profile"

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    updated_at = mapped_column(DateTime)
    values_count = mapped_column(Integer)
    values_percentage = mapped_column(Float)
    valid_count = mapped_column(Integer)
    duplicate_count = mapped_column(Integer)
    null_count = mapped_column(Integer)
    null_proportion = mapped_column(Float)
    missing_percentage = mapped_column(Float)
    missing_count = mapped_column(Integer)
    unique_count = mapped_column(Integer)
    unique_proportion = mapped_column(Float)
    distinct_count = mapped_column(Integer)
    distinct_proportion = mapped_column(Float)
    min = mapped_column(String(200))
    max = mapped_column(String(200))
    min_length = mapped_column(Integer)
    max_length = mapped_column(Integer)
    mean = mapped_column(Float)
    sum = mapped_column(Float)
    stddev = mapped_column(Float)
    variance = mapped_column(Float)
    median = mapped_column(Float)
    first_quartile = mapped_column(Float)
    third_quartile = mapped_column(Float)
    inter_quartile_range = mapped_column(Float)
    non_parametric_skew = mapped_column(Float)
    histogram = mapped_column(JSON)

    # Associations
    column_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_table_column.id", name="fk_column_profile_column_id"),
        nullable=False,
        index=True,
    )
    column = relationship("TableColumn", foreign_keys=[column_id])
    table_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_database_table.id", name="fk_column_profile_table_id"),
        nullable=False,
        index=True,
    )
    table = relationship("DatabaseTable", foreign_keys=[table_id])

    def __str__(self):
        return str("")

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class Role(Base):
    """Perfil de usuário"""

    __tablename__ = "tb_role"

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    name = mapped_column(String(200), nullable=False)
    deleted = mapped_column(
        Boolean, default=False, nullable=False, server_default="False"
    )

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class Action(Base):
    """Ação associada aos objetos"""

    __tablename__ = "tb_action"

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    name = mapped_column(String(200), nullable=False)
    deleted = mapped_column(
        Boolean, default=False, nullable=False, server_default="False"
    )
    applies_to = mapped_column(String(200), nullable=False)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class TableRole(Base):
    """Associação entre as entidades Table, Role e Action"""

    __tablename__ = "tb_table_role"

    # Fields
    id = mapped_column(Integer, primary_key=True)
    parameters = mapped_column(JSON)

    # Associations
    table_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_database_table.id", name="fk_table_role_table_id"),
        nullable=False,
        index=True,
    )
    table = relationship("DatabaseTable", foreign_keys=[table_id])
    role_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_role.id", name="fk_table_role_role_id"),
        nullable=False,
        index=True,
    )
    role = relationship("Role", foreign_keys=[role_id])
    action_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_action.id", name="fk_table_role_action_id"),
        nullable=False,
        index=True,
    )
    action = relationship("Action", foreign_keys=[action_id])

    def __str__(self):
        return str("")

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class AIModel(Asset):
    """Modelo de inteligência artificial"""

    __tablename__ = "tb_a_i_model"

    # Fields
    id = mapped_column(
        ForeignKey("tb_asset.id"),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    type = mapped_column(String(200), nullable=False)
    algorithms = mapped_column(String(500))
    technologies = mapped_column(String(1000))
    server = mapped_column(String(1000))
    source = mapped_column(String(1000))

    # Associations
    attributes = relationship("AIModelAttribute", lazy="joined")

    __mapper_args__ = {
        "polymorphic_identity": "model",
        "inherit_condition": (id == Asset.id),
    }
    hyper_parameters = relationship("AIModelHyperParameter", lazy="joined")

    __mapper_args__ = {
        "polymorphic_identity": "model",
        "inherit_condition": (id == Asset.id),
    }
    results = relationship("AIModelResult", lazy="joined")

    __mapper_args__ = {
        "polymorphic_identity": "model",
        "inherit_condition": (id == Asset.id),
    }

    def __str__(self):
        return str("")

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class AIModelAttribute(Base):
    """Atributo (coluna) usada como feature ou rótulo no modelo"""

    __tablename__ = "tb_a_i_model_attribute"

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    name = mapped_column(String(200), nullable=False)
    description = mapped_column(String(8000))
    deleted = mapped_column(
        Boolean, default=False, nullable=False, server_default="False"
    )
    usage = mapped_column(String(100), default="feature", nullable=False)

    # Associations
    model_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_a_i_model.id", name="fk_a_i_model_attribute_model_id"),
        nullable=False,
        index=True,
    )

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class AIModelHyperParameter(Base):
    """Hiper parâmetro usado no modelo"""

    __tablename__ = "tb_a_i_model_hyper_parameter"

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    name = mapped_column(String(200), nullable=False)
    description = mapped_column(String(8000))
    value = mapped_column(JSON)

    # Associations
    model_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "tb_a_i_model.id", name="fk_a_i_model_hyper_parameter_model_id"
        ),
        nullable=False,
        index=True,
    )

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class AIModelResult(Base):
    """Resultado no modelo. Pode ser métrica ou outra informação."""

    __tablename__ = "tb_a_i_model_result"

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    name = mapped_column(String(200), nullable=False)
    type = mapped_column(String(100), nullable=False)
    value = mapped_column(JSON)

    # Associations
    model_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_a_i_model.id", name="fk_a_i_model_result_model_id"),
        nullable=False,
        index=True,
    )

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"
