"""phase_4a_onboarding_tables

Revision ID: a1b2c3d4e5f6
Revises: 973e9bef3510
Create Date: 2026-10-21 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '973e9bef3510'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create onboarding_sessions and onboarding_turns tables."""
    op.create_table(
        'onboarding_sessions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('status', sa.String(length=32), server_default='in_progress', nullable=False),
        sa.Column('current_question', sa.Text(), nullable=True),
        sa.Column('current_question_category', sa.String(length=64), nullable=True),
        sa.Column('turn_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column(
            'collected_facts',
            postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'),
            server_default=sa.text("'{}'"),
            nullable=True,
        ),
        sa.Column(
            'areas_covered',
            postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'),
            server_default=sa.text("'[]'"),
            nullable=True,
        ),
        sa.Column(
            'ai_summary',
            postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'),
            nullable=True,
        ),
        sa.Column('summary_generated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_summary_confirmed', sa.Boolean(), server_default=sa.text('FALSE'), nullable=False),
        sa.Column('summary_confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint(
            "status IN ('not_started', 'in_progress', 'awaiting_confirmation', 'completed')",
            name='onboarding_status_check',
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index('onboarding_sessions_user_id_idx', 'onboarding_sessions', ['user_id'], unique=True)

    op.create_table(
        'onboarding_turns',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('session_id', sa.Uuid(), nullable=False),
        sa.Column('turn_number', sa.Integer(), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('question_category', sa.String(length=64), nullable=False),
        sa.Column('user_response', sa.Text(), nullable=True),
        sa.Column(
            'extracted_facts',
            postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'),
            nullable=True,
        ),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['onboarding_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('onboarding_turns_session_idx', 'onboarding_turns', ['session_id'])
    op.create_index('onboarding_turns_session_turn_idx', 'onboarding_turns', ['session_id', 'turn_number'], unique=True)


def downgrade() -> None:
    """Drop onboarding tables."""
    op.drop_index('onboarding_turns_session_turn_idx', table_name='onboarding_turns')
    op.drop_index('onboarding_turns_session_idx', table_name='onboarding_turns')
    op.drop_table('onboarding_turns')
    op.drop_index('onboarding_sessions_user_id_idx', table_name='onboarding_sessions')
    op.drop_table('onboarding_sessions')
