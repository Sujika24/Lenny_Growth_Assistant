"""initial_schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-10-11 19:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'sessions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.String(length=64), nullable=False, server_default='anonymous'),
        sa.Column('provider', sa.String(length=32), nullable=False, server_default='ollama'),
        sa.Column('model_name', sa.String(length=64), nullable=False, server_default='llama3.2:3b'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'messages',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('session_id', sa.String(length=36), sa.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(length=16), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('citations', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'artifacts',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('session_id', sa.String(length=36), sa.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('message_id', sa.String(length=36), sa.ForeignKey('messages.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('artifact_type', sa.String(length=32), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('artifacts')
    op.drop_table('messages')
    op.drop_table('sessions')
