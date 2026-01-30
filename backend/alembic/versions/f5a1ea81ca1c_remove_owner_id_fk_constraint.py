"""remove_owner_id_fk_constraint

Revision ID: f5a1ea81ca1c
Revises: 6f33e21a25cd
Create Date: 2026-01-29 15:14:33.168786

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5a1ea81ca1c'
down_revision: Union[str, Sequence[str], None] = '6f33e21a25cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('db_connection_ibfk_1', 'db_connection', type_='foreignkey')


def downgrade() -> None:
    """Downgrade schema."""
    op.create_foreign_key('db_connection_ibfk_1', 'db_connection', 'user', ['owner_id'], ['id'])
