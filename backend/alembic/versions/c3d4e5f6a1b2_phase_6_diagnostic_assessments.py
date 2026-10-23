"""phase_6_diagnostic_assessments

Revision ID: c3d4e5f6a1b2
Revises: b2c3d4e5f6a1
Create Date: 2026-10-22 23:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a1b2'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add topic to assessment_questions, question_ids to assessment_attempts, and breakdowns to assessment_results."""
    op.add_column(
        'assessment_questions',
        sa.Column(
            'topic',
            sa.String(length=128),
            server_default=sa.text("'General'"),
            nullable=False,
        ),
    )
    op.add_column(
        'assessment_attempts',
        sa.Column(
            'question_ids',
            postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'),
            server_default=sa.text("'[]'"),
            nullable=True,
        ),
    )
    op.add_column(
        'assessment_results',
        sa.Column(
            'topic_breakdown',
            postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'),
            server_default=sa.text("'[]'"),
            nullable=True,
        ),
    )
    op.add_column(
        'assessment_results',
        sa.Column(
            'difficulty_breakdown',
            postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'),
            server_default=sa.text("'{}'"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Revert diagnostic assessment enhancements."""
    op.drop_column('assessment_results', 'difficulty_breakdown')
    op.drop_column('assessment_results', 'topic_breakdown')
    op.drop_column('assessment_attempts', 'question_ids')
    op.drop_column('assessment_questions', 'topic')
