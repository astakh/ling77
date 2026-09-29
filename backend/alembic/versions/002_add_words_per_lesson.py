"""add words_per_lesson to learning_profiles

Revision ID: 002_add_words_per_lesson
Revises: 001_initial
Create Date: 2026-09-29 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_words_per_lesson'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('learning_profiles', sa.Column('words_per_lesson', sa.Integer(), nullable=False, server_default='8'))


def downgrade() -> None:
    op.drop_column('learning_profiles', 'words_per_lesson')
