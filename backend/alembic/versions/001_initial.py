"""initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('timezone', sa.String(64), nullable=False, server_default='Europe/Moscow'),
        sa.Column('is_onboarded', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # Dictionaries table
    op.create_table(
        'dictionaries',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # Learning profiles table
    op.create_table(
        'learning_profiles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('level', sa.String(2), nullable=False),
        sa.Column('dictionary_id', sa.Integer(), sa.ForeignKey('dictionaries.id'), nullable=True),
        sa.Column('daily_lesson_limit', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('last_lesson_number', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # Words table
    op.create_table(
        'words',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('lemma', sa.String(255), nullable=False),
        sa.Column('lemma_key', sa.String(255), nullable=False),
        sa.Column('pos', sa.String(32), nullable=False),
        sa.Column('level', sa.String(2), nullable=False),
        sa.Column('translations', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('dictionary_id', sa.Integer(), sa.ForeignKey('dictionaries.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('lemma_key', 'pos', name='uq_words_lemma_pos'),
    )
    op.create_index('ix_words_dictionary_level', 'words', ['dictionary_id', 'level'])

    # User words table
    op.create_table(
        'user_words',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('learning_profile_id', sa.Integer(), sa.ForeignKey('learning_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('word_id', sa.Integer(), sa.ForeignKey('words.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(16), nullable=False, server_default='active'),
        sa.Column('stage', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('due_lesson_number', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('learning_profile_id', 'word_id', name='uq_user_words_profile_word'),
    )
    op.create_index('ix_user_words_due', 'user_words', ['learning_profile_id', 'due_lesson_number'])

    # Lessons table
    op.create_table(
        'lessons',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('learning_profile_id', sa.Integer(), sa.ForeignKey('learning_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('lesson_number', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(16), nullable=False, server_default='in_progress'),
        sa.Column('started_local_date', sa.String(10), nullable=False),
        sa.Column('completed_local_date', sa.String(10), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('learning_profile_id', 'lesson_number', name='uq_lessons_profile_number'),
    )
    # Partial unique index for in_progress lessons
    op.create_index(
        'uq_lessons_in_progress',
        'lessons',
        ['learning_profile_id'],
        unique=True,
        postgresql_where=sa.text("status = 'in_progress'")
    )

    # Lesson exercises table
    op.create_table(
        'lesson_exercises',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('lesson_id', sa.Integer(), sa.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('target_sentence', sa.Text(), nullable=False),
        sa.Column('reference_translation', sa.Text(), nullable=False),
        sa.Column('user_translation', sa.Text(), nullable=True),
        sa.Column('status', sa.String(16), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('lesson_id', 'order_index', name='uq_exercises_lesson_order'),
    )

    # Lesson exercise words table
    op.create_table(
        'lesson_exercise_words',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('exercise_id', sa.Integer(), sa.ForeignKey('lesson_exercises.id', ondelete='CASCADE'), nullable=False),
        sa.Column('word_id', sa.Integer(), sa.ForeignKey('words.id', ondelete='CASCADE'), nullable=False),
        sa.Column('is_target', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('is_new', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('surface_form', sa.String(255), nullable=False),
        sa.Column('result', sa.String(16), nullable=True),
        sa.Column('user_fragment', sa.String(255), nullable=True),
        sa.Column('stage_before', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('stage_after', sa.Integer(), nullable=False, server_default='0'),
    )

    # Refresh tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False, unique=True),
        sa.Column('family_id', sa.String(64), nullable=False, index=True),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_refresh_tokens_token_hash', 'refresh_tokens', ['token_hash'])

    # LLM calls table
    op.create_table(
        'llm_calls',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('purpose', sa.String(64), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('lesson_id', sa.Integer(), sa.ForeignKey('lessons.id', ondelete='SET NULL'), nullable=True),
        sa.Column('request', postgresql.JSONB(), nullable=False),
        sa.Column('response', postgresql.JSONB(), nullable=True),
        sa.Column('status', sa.String(16), nullable=False),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('tokens', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_llm_calls_created', 'llm_calls', ['created_at'])

    # Events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('event_type', sa.String(64), nullable=False, index=True),
        sa.Column('payload', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('events')
    op.drop_table('llm_calls')
    op.drop_table('refresh_tokens')
    op.drop_table('lesson_exercise_words')
    op.drop_table('lesson_exercises')
    op.drop_index('uq_lessons_in_progress', table_name='lessons')
    op.drop_table('lessons')
    op.drop_index('ix_user_words_due', table_name='user_words')
    op.drop_table('user_words')
    op.drop_index('ix_words_dictionary_level', table_name='words')
    op.drop_table('words')
    op.drop_table('learning_profiles')
    op.drop_table('dictionaries')
    op.drop_table('users')
