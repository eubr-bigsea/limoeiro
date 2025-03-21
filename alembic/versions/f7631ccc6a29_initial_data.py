"""Initial data

Revision ID: f7631ccc6a29
Revises: e28787a3c49f

"""
import uuid
from typing import Sequence, Union

from alembic import op
from sqlalchemy.orm import Session
from app.models import ResponsibilityType, DatabaseProviderType

# revision identifiers, used by Alembic.
revision: str = "f7631ccc6a29"
down_revision: Union[str, None] = "e28787a3c49f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)

    session.add_all(
        [
            DatabaseProviderType(
                id="POSTGRESQL",
                display_name="PostgreSQL",
                image="postgresql",
                supports_schema=True,
            ),
            DatabaseProviderType(
                id="HIVE",
                display_name="Hive",
                image="hive",
                supports_schema=False,
            ),
            DatabaseProviderType(
                id="DRUID",
                display_name="Druid",
                image="druid",
                supports_schema=False,
            ),
            DatabaseProviderType(
                id="ELASTICSEARCH",
                display_name="Elasticsearch",
                image="elasticsearch",
                supports_schema=False,
            ),
            DatabaseProviderType(
                id="OPENSEARCH",
                display_name="Opensearch",
                image="opensearch",
                supports_schema=False,
            ),
            DatabaseProviderType(
                id="MYSQL",
                display_name="MySQL",
                image="mysql",
                supports_schema=False,
            ),
            DatabaseProviderType(
                id="MARIADB",
                display_name="MariaDB",
                image="mariadb",
                supports_schema=False,
            ),
            DatabaseProviderType(
                id="ORACLE",
                display_name="Oracle",
                image="oracle",
                supports_schema=True,
            ),
            DatabaseProviderType(
                id="MONGODB",
                display_name="MongoDB",
                image="mongodb",
                supports_schema=False,
            ),
            DatabaseProviderType(
                id="SQLSERVER",
                display_name="SQL Server",
                image="sql-server",
                supports_schema=True,
            ),
            ResponsibilityType(
                id=uuid.UUID("f319d911-fd20-4606-a7c1-3e06e864057f"),
                name="Técnica",
                description="Responsável técnico",
                deleted=False,
            ),
            ResponsibilityType(
                id=uuid.UUID("727d761b-824f-4582-9919-4513fa87584e"),
                name="Jurídica",
                description="Responsável jurídico",
                deleted=False,
            ),
        ]
    )

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    (
        session.query(DatabaseProviderType)
        .filter(
            DatabaseProviderType.id.in_(
                [
                    "POSTGRESQL",
                    "HIVE",
                    "DRUID",
                    "ELASTICSEARCH",
                    "OPENSEARCH",
                    "MYSQL",
                    "MARIADB",
                    "ORACLE",
                    "MONGODB",
                    "SQLSERVER",
                ]
            )
        )
        .delete(synchronize_session=False)
    )
    (
        session.query(ResponsibilityType)
        .filter(
            ResponsibilityType.id.in_(
                [
                    uuid.UUID("f319d911-fd20-4606-a7c1-3e06e864057f"),
                    uuid.UUID("727d761b-824f-4582-9919-4513fa87584e"),
                ]
            )
        )
        .delete(synchronize_session=False)
    )

    session.commit()
