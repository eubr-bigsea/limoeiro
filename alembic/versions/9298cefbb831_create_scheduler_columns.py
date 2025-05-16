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


scheduling_type_enum = sa.Enum('MANUAL', 'CRON', name='SchedulingTypeEnumType')

def upgrade():
    scheduling_type_enum.create(op.get_bind())

    op.add_column(
        'tb_database_provider_ingestion',
        sa.Column('scheduling_type', scheduling_type_enum, nullable=False,server_default='MANUAL')
    )

def downgrade():
    op.drop_column('tb_database_provider_ingestion', 'scheduling_type')

    scheduling_type_enum.drop(op.get_bind())