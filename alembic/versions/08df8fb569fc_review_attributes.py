"""Review attributes

Revision ID: 08df8fb569fc
Revises: f2d8ddc8ad77
Create Date: 2025-02-21 17:47:09.195577

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08df8fb569fc'
down_revision: Union[str, None] = 'f2d8ddc8ad77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_tb_database_provider_connection_provider_id', table_name='tb_database_provider_connection')
    op.drop_constraint('fk_database_provider_connection_provider_id', 'tb_database_provider_connection', type_='foreignkey')
    op.drop_column('tb_database_provider_connection', 'provider_id')
    op.add_column('tb_i_a_model', sa.Column('technology', sa.String(length=200), nullable=True))
    op.drop_column('tb_i_a_model', 'tecnology')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tb_i_a_model', sa.Column('tecnology', sa.VARCHAR(length=200), autoincrement=False, nullable=True))
    op.drop_column('tb_i_a_model', 'technology')
    op.add_column('tb_database_provider_connection', sa.Column('provider_id', sa.UUID(), autoincrement=False, nullable=False))
    op.create_foreign_key('fk_database_provider_connection_provider_id', 'tb_database_provider_connection', 'tb_database_provider', ['provider_id'], ['id'])
    op.create_index('ix_tb_database_provider_connection_provider_id', 'tb_database_provider_connection', ['provider_id'], unique=False)
    # ### end Alembic commands ###
