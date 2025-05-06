"""add current_round_number to solo_rooms

Revision ID: 48fd69410aa6
Revises: 39dfdcbb813c
Create Date: 2025-05-06 06:42:45.490206

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '48fd69410aa6'
down_revision: Union[str, None] = '39dfdcbb813c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.add_column('solo_rooms', sa.Column('current_round_number', sa.Integer(), nullable=False, server_default='1'))

def downgrade():
    op.drop_column('solo_rooms', 'current_round_number')


def downgrade() -> None:
    pass
