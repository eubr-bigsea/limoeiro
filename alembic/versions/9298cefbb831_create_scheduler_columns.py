"""create scheduler columns

Revision ID: 9298cefbb831
Revises: 1a0c723a8420
Create Date: 2025-05-13 18:42:42.194814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9298cefbb831'
down_revision: Union[str, None] = '1a0c723a8420'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tb_database_provider_ingestion', sa.Column('scheduling_type', sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column('tb_database_provider_ingestion', 'scheduling_type')