"""alter_queryhistory_user_id_string

Revision ID: 67f79582929f
Revises: d3aea1266440
Create Date: 2026-01-30 23:21:18.786854

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67f79582929f'
down_revision: Union[str, Sequence[str], None] = 'd3aea1266440'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
