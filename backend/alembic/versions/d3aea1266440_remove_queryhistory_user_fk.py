"""remove_queryhistory_user_fk

Revision ID: d3aea1266440
Revises: f5a1ea81ca1c
Create Date: 2026-01-30 23:12:04.673739

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3aea1266440'
down_revision: Union[str, Sequence[str], None] = 'f5a1ea81ca1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop the user_id foreign key constraint from queryhistory table."""
    op.drop_constraint('queryhistory_ibfk_2', 'queryhistory', type_='foreignkey')


def downgrade() -> None:
    """Recreate the user_id foreign key constraint on queryhistory table."""
    op.create_foreign_key(
        'queryhistory_ibfk_2',
        'queryhistory',
        'user',
        ['user_id'],
        ['id']
    )
