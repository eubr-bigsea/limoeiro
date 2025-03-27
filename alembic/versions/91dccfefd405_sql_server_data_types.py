"""sql server data_types

Revision ID: 91dccfefd405
Revises: 342d16d3bbe5
Create Date: 2025-03-24 21:28:11.040661

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91dccfefd405'
down_revision: Union[str, None] = '342d16d3bbe5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TYPE \"DataTypeEnumType\" ADD VALUE 'NVARCHAR'")
    op.execute("ALTER TYPE \"DataTypeEnumType\" ADD VALUE 'NCHAR'")
    op.execute("ALTER TYPE \"DataTypeEnumType\" ADD VALUE 'MONEY'")
    op.execute("ALTER TYPE \"DataTypeEnumType\" ADD VALUE 'BIT'")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # op.execute("ALTER TYPE \"DataTypeEnumType\" REMOVE VALUE 'NVARCHAR'")
    # op.execute("ALTER TYPE \"DataTypeEnumType\" REMOVE VALUE 'NCHAR'")
    # op.execute("ALTER TYPE \"DataTypeEnumType\" REMOVE VALUE 'MONEY'")
    # op.execute("ALTER TYPE \"DataTypeEnumType\" REMOVE VALUE 'BIT'")
    # ### end Alembic commands ###
    pass
