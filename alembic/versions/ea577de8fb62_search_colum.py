"""internal_table

Revision ID: ea577de8fb62
Revises: a0e748bf1825
Create Date: 2025-06-03 23:17:50.916978

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ea577de8fb62'
down_revision: Union[str, None] = 'a0e748bf1825'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###   
    op.add_column('tb_table_column', sa.Column('search', postgresql.TSVECTOR(), nullable=True))
    op.create_index('ix_search_search_column', 'tb_table_column', ['search'], unique=False, postgresql_using='gin')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###    
    op.drop_index('ix_search_search_column', table_name='tb_table_column', postgresql_using='gin')
    op.drop_column('tb_table_column', 'search')
    # ### end Alembic commands ###