"""Create wallet table

Revision ID: 001
Revises:
Create Date: 2026-04-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

def upgrade():
    op.create_table(
        'wallets',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('balance', sa.Numeric(precision=15, scale=2), default=0.00)
    )

def downgrade():
    op.drop_table('wallets')