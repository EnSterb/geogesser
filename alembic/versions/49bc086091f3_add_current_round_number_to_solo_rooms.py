"""add current_round_number to solo_rooms

Revision ID: 49bc086091f3
Revises: 48fd69410aa6
Create Date: 2025-05-06 06:49:14.781114

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '49bc086091f3'
down_revision: Union[str, None] = '48fd69410aa6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('solo_rooms', sa.Column('current_round_number', sa.Integer(), nullable=False, server_default='1'))
    op.alter_column('solo_rooms', 'current_round_number', server_default=None)

def downgrade():
    op.drop_column('solo_rooms', 'current_round_number')

