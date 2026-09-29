"""add is_public to dictionaries

Revision ID: 003_add_is_public
Revises: 002_add_words_per_lesson
Create Date: 2026-09-29 16:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_add_is_public'
down_revision = '002_add_words_per_lesson'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем поле is_public с дефолтным значением True
    op.add_column('dictionaries', sa.Column('is_public', sa.Boolean(), nullable=False, server_default='true'))
    
    # Скрываем "Общий словарь" от пользователей
    op.execute("UPDATE dictionaries SET is_public = false WHERE name = 'Общий словарь'")


def downgrade() -> None:
    op.drop_column('dictionaries', 'is_public')
