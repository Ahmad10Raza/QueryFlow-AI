"""create_query_request_table

Revision ID: ba19e5a9fd71
Revises: 67f79582929f
Create Date: 2026-01-31 00:09:26.313856

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba19e5a9fd71'
down_revision: Union[str, Sequence[str], None] = '67f79582929f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create queryrequest table for approval workflow."""
    op.create_table(
        'queryrequest',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('connection_id', sa.Integer(), sa.ForeignKey('db_connection.id'), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('generated_sql', sa.Text(), nullable=False),
        sa.Column('intent', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='PENDING'),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_queryrequest_user_id', 'queryrequest', ['user_id'])
    op.create_index('ix_queryrequest_status', 'queryrequest', ['status'])


def downgrade() -> None:
    """Drop queryrequest table."""
    op.drop_index('ix_queryrequest_status', 'queryrequest')
    op.drop_index('ix_queryrequest_user_id', 'queryrequest')
    op.drop_table('queryrequest')
