"""Unique

Revision ID: cc76a21e7a52
Revises: ceca30ce6e89
Create Date: 2025-03-07 20:31:38.153985

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc76a21e7a52'
down_revision: Union[str, None] = 'ceca30ce6e89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tb_database_provider', sa.Column('cron_expression', sa.String()))


def downgrade() -> None:
    op.drop_column('tb_database_provider', 'cron_expression') 
