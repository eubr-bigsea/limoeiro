import enum
import uuid
from datetime import datetime, timezone
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
    Table,
    Index,
    event,
    Column,
)
from sqlalchemy.types import UUID
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.sql.expression import func

from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.dialects.postgresql import JSONB


def utc_now() -> datetime:
    """Utility function to get current date as UTC"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


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
    BIT = "BIT"
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
    MONEY = "MONEY"
    NCHAR = "NCHAR"
    NTEXT = "NTEXT"
    NULL = "NULL"
    NUMBER = "NUMBER"
    NUMERIC = "NUMERIC"
    NVARCHAR = "NVARCHAR"
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


class SchedulingType(str, enum.Enum):
    MANUAL = "MANUAL"
    CRON = "CRON"

    @staticmethod
    def values():
        return [item.value for item in SchedulingType]


# Association Table for Many-to-Many Relationship
role_permission = Table(
    "tb_role_permission",
    Base.metadata,
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("tb_role.id"),
        nullable=False,
        primary_key=True,
    ),
    Column(
        "tb_permission_id",
        String(100),
        ForeignKey("tb_permission.id"),
        nullable=False,
        primary_key=True,
    ),
)
# Association Table for Many-to-Many Relationship
user_role = Table(
    "tb_user_role",
    Base.metadata,
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("tb_role.id"),
        nullable=False,
        primary_key=True,
    ),
    Column(
        "tb_user_id",
        UUID(as_uuid=True),
        ForeignKey("tb_user.id"),
        nullable=False,
        primary_key=True,
    ),
)

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


class Permission(Base):
    """Permission in Lemonade"""

    __tablename__ = "tb_permission"

    # Fields
    id = mapped_column(
        String(100),
        primary_key=True,
        autoincrement=False,
    )
    description = mapped_column(String(100), nullable=False)
    enabled = mapped_column(Boolean, default=True, nullable=False)
    applicable_to = mapped_column(String(40))

    def __str__(self):
        return str("")

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class Role(Base):
    """Roles in Lemonade"""

    __tablename__ = "tb_role"

    # Fields
    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    name = mapped_column(String(100), nullable=False)
    description = mapped_column(String(250))
    all_user = mapped_column(Boolean, default=False, nullable=False)
    system = mapped_column(Boolean, default=False, nullable=False)
    deleted = mapped_column(Boolean, default=False, nullable=False)

    # Associations
    permissions = relationship(
        "Permission",
        overlaps="roles",
        secondary=role_permission,
        cascade="save-update",
        lazy="joined",
    )
    users = relationship(
        "User",
        overlaps="roles",
        secondary=user_role,
        cascade="save-update",
        lazy="joined",
    )

    def __str__(self):
        return str("")

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


class Contact(Base):
    """Contato"""

    __tablename__ = "tb_contact"

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
    phone_number = mapped_column(String(40))
    cell_phone_number = mapped_column(String(40))
    email = mapped_column(String(250))
    type = mapped_column(String(50), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "contact",
        "polymorphic_on": type,
    }

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class Company(Contact):
    """Empresa"""

    __tablename__ = "tb_company"

    # Fields
    id = mapped_column(
        ForeignKey("tb_contact.id"),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    organization = mapped_column(String(100))
    document = mapped_column(String(100))
    document_type = mapped_column(String(20), default="CNPJ")
    contact_name = mapped_column(String(100))

    __mapper_args__ = {
        "polymorphic_identity": "company",
        "inherit_condition": (id == Contact.id),
    }

    def __str__(self):
        return str("")

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class Person(Contact):
    """Pessoa"""

    __tablename__ = "tb_person"

    # Fields
    id = mapped_column(
        ForeignKey("tb_contact.id"),
        primary_key=True,
        autoincrement=False,
        default=uuid.uuid4,
    )
    organization = mapped_column(String(100))
    document = mapped_column(String(100))
    document_type = mapped_column(String(20), default="CPF")
    company = mapped_column(String(200))

    # Associations
    user_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_user.id", name="fk_person_user_id"),
        index=True,
    )
    user = relationship("User", foreign_keys=[user_id])

    __mapper_args__ = {
        "polymorphic_identity": "person",
        "inherit_condition": (id == Contact.id),
    }

    def __str__(self):
        return str("")

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class Responsibility(Base):
    """Responsabilidade"""

    __tablename__ = "tb_responsibility"
    __table_args__ = (
        PrimaryKeyConstraint("asset_id", "contact_id", "type_id"),
        UniqueConstraint(
            "asset_id", "contact_id", "type_id", name="inx_uq_responsibility"
        ),
    )

    # Fields

    # Associations
    contact_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_contact.id", name="fk_responsibility_contact_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    contact = relationship("Contact", foreign_keys=[contact_id])
    type_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "tb_responsibility_type.id", name="fk_responsibility_type_id"
        ),
        primary_key=True,
        nullable=False,
        index=True,
    )
    type = relationship("ResponsibilityType", foreign_keys=[type_id])
    asset_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_asset.id", name="fk_responsibility_asset_id"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    asset = relationship("Asset", foreign_keys=[asset_id])

    def __str__(self):
        return str("Responsibility")

    def __repr__(self):
        return f"<Instance {self.__class__}>"


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
    supports_schema = mapped_column(Boolean, default=True, nullable=False)

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


class AssetTag(Base):
    """Tags associadas aos ativos"""

    __tablename__ = "tb_asset_tag"
    __table_args__ = (PrimaryKeyConstraint("asset_id", "tag_id"),)

    # Fields

    # Associations
    asset_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_asset.id", name="fk_asset_tag_asset_id"),
        nullable=False,
        index=True,
    )
    asset = relationship("Asset", foreign_keys=[asset_id], lazy="joined")
    tag_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tb_tag.id", name="fk_asset_tag_tag_id"),
        nullable=False,
        index=True,
    )
    tag = relationship("Tag", foreign_keys=[tag_id], lazy="joined")

    def __str__(self):
        return str("AssetTag")

    def __repr__(self):
        return f"<Instance {self.__class__}>"


class Asset(Base):
    """Ativo no catalogo de dados"""

    __tablename__ = "tb_asset"
    __table_args__ = (
        UniqueConstraint(
            "fully_qualified_name", "asset_type", name="inx_uq_asset"
        ),
        Index("ix_search_search", "search", postgresql_using="gin"),
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
    tree = mapped_column(JSONB)
    search = mapped_column(TSVECTOR)

    # Associations
    domain_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "tb_domain.id", name="fk_asset_domain_id", ondelete="set null"
        ),
        index=True,
    )
    domain = relationship("Domain", foreign_keys=[domain_id], lazy="joined")
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

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


@event.listens_for(Asset, "before_insert", propagate=True)
@event.listens_for(Asset, "before_update", propagate=True)
def update_search(mapper, connection, target: Asset):
    target.search = func.to_tsvector(
        "portuguese", f"{target.name} {target.description} {target.notes}"
    )
    return
    match target:
        case Database():
            target.tree = {
                "database_provider": {
                    "id": str(target.provider.id),
                    "name": target.provider.name,
                }
            }
        case DatabaseSchema():
            target.tree = {
                "database": {
                    "id": str(target.database.id),
                    "name": target.database.name,
                },
                "database_provider": {
                    "id": str(target.database.provider.id),
                    "name": target.database.provider.name,
                },
            }
        case DatabaseTable():
            target.tree = {
                "database": {
                    "id": str(target.database.id),
                    "name": target.database.name,
                },
                "database_provider": {
                    "id": str(target.database.provider.id),
                    "name": target.database.provider.name,
                },
                "database_schema": {
                    "id": str(target.database_schema.id),
                    "name": target.database_schema.name,
                },
            }


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
        onupdate="CASCADE",
        index=True,
    )
    provider_type = relationship(
        "DatabaseProviderType", foreign_keys=[provider_type_id], lazy="joined"
    )

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

    # Associations
    provider_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "tb_database_provider.id",
            name="fk_database_provider_connection_provider_id",
        ),
        nullable=False,
        index=True,
    )
    provider = relationship("DatabaseProvider", foreign_keys=[provider_id])

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
    scheduling = mapped_column(String(200))
    scheduling_type = mapped_column(
        Enum(SchedulingType, name="SchedulingTypeEnumType"), default="MANUAL"
    )
    recent_runs_statuses = mapped_column(String(100))
    retries = mapped_column(Integer, default=5, nullable=False)
    collect_sample = mapped_column(Boolean, default=False, nullable=False)
    apply_semantic_analysis = mapped_column(
        Boolean, default=False, nullable=False
    )

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
    provider = relationship("DatabaseProvider", foreign_keys=[provider_id])

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class DatabaseProviderIngestionExecution(Base):
    """Execução de ingestão"""

    __tablename__ = "tb_database_provider_ingestion_execution"

    # Fields
    id = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    created_at = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at = mapped_column(DateTime, default=utc_now, onupdate=utc_now)
    status = mapped_column(String(100), nullable=False)
    job_id = mapped_column(Integer)
    finished = mapped_column(DateTime)
    trigger_mode = mapped_column(String(50), nullable=False)

    # Associations
    triggered_by_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "tb_user.id",
            name="fk_database_provider_ingestion_execution_triggered_by_id",
        ),
        index=True,
    )
    triggered_by = relationship("User", foreign_keys=[triggered_by_id])
    ingestion_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "tb_database_provider_ingestion.id",
            name="fk_database_provider_ingestion_execution_ingestion_id",
        ),
        nullable=False,
        index=True,
    )
    ingestion = relationship(
        "DatabaseProviderIngestion", foreign_keys=[ingestion_id], lazy="joined"
    )
    logs = relationship(
        "DatabaseProviderIngestionLog",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def __str__(self):
        return str("")

    def __repr__(self):
        return f"<Instance {self.__class__}: {self.id}>"


class DatabaseProviderIngestionLog(Base):
    """Log de execução de ingestão"""

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
        "DatabaseProviderIngestion", foreign_keys=[ingestion_id]
    )
    execution_id = mapped_column(
        Integer,
        ForeignKey(
            "tb_database_provider_ingestion_execution.id",
            name="fk_database_provider_ingestion_log_execution_id",
        ),
        nullable=False,
        index=True,
    )
    execution = relationship(
        "DatabaseProviderIngestionExecution",
        back_populates="logs",
        foreign_keys=[execution_id],
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
    database_schema_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "tb_database_schema.id", name="fk_database_table_database_schema_id"
        ),
        index=True,
    )
    database_schema = relationship(
        "DatabaseSchema", foreign_keys=[database_schema_id], lazy="joined"
    )
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
    sample_date = mapped_column(DateTime, nullable=False)
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
    semantic_type = mapped_column(String(200))
    default_value = mapped_column(String(200))

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
        return f"<Instance {self.__class__}>"


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
    hyper_parameters = relationship("AIModelHyperParameter", lazy="joined")
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
