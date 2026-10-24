"""phase_9a_job_matching_engine

Revision ID: a2b3c4d5e6f7
Revises: f6a1b2c3d4e5
Create Date: 2026-10-24 20:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a2b3c4d5e6f7'
down_revision: Union[str, Sequence[str], None] = 'f6a1b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Enhance job_matches schema with multi-factor scores, evidence coverage, staleness, and detailed skill sets."""
    # 1. Add score breakdown and confidence columns
    op.add_column('job_matches', sa.Column('project_score', sa.Numeric(precision=4, scale=1), server_default='0.0', nullable=False))
    op.add_column('job_matches', sa.Column('location_score', sa.Numeric(precision=4, scale=1), server_default='0.0', nullable=False))
    op.add_column('job_matches', sa.Column('preference_score', sa.Numeric(precision=4, scale=1), server_default='0.0', nullable=False))
    op.add_column('job_matches', sa.Column('evidence_coverage', sa.Numeric(precision=4, scale=1), server_default='0.0', nullable=False))
    op.add_column('job_matches', sa.Column('scoring_version', sa.String(length=32), server_default='v1.0', nullable=False))
    op.add_column('job_matches', sa.Column('is_stale', sa.Boolean(), server_default=sa.text('FALSE'), nullable=False))

    # 2. Add detailed skill arrays
    op.add_column(
        'job_matches',
        sa.Column(
            'matched_preferred_skills',
            postgresql.ARRAY(sa.String(length=64)).with_variant(sa.JSON(), 'sqlite'),
            server_default=sa.text("'{}'"),
            nullable=False
        )
    )
    op.add_column(
        'job_matches',
        sa.Column(
            'unknown_skills',
            postgresql.ARRAY(sa.String(length=64)).with_variant(sa.JSON(), 'sqlite'),
            server_default=sa.text("'{}'"),
            nullable=False
        )
    )

    # 3. Add index on is_stale for fast stale match retrieval
    op.create_index('job_matches_is_stale_idx', 'job_matches', ['is_stale'], unique=False)


def downgrade() -> None:
    """Revert Phase 9A job_matches schema extensions."""
    op.drop_index('job_matches_is_stale_idx', table_name='job_matches')
    op.drop_column('job_matches', 'unknown_skills')
    op.drop_column('job_matches', 'matched_preferred_skills')
    op.drop_column('job_matches', 'is_stale')
    op.drop_column('job_matches', 'scoring_version')
    op.drop_column('job_matches', 'evidence_coverage')
    op.drop_column('job_matches', 'preference_score')
    op.drop_column('job_matches', 'location_score')
    op.drop_column('job_matches', 'project_score')
