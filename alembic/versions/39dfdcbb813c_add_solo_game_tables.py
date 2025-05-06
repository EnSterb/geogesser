"""add solo game tables

Revision ID: 39dfdcbb813c
Revises: 5c7b2431c8af
Create Date: 2025-05-06 01:13:02.659094

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39dfdcbb813c'
down_revision: Union[str, None] = '5c7b2431c8af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
