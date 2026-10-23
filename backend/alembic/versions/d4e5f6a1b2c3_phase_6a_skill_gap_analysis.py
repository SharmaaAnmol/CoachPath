"""phase_6a_skill_gap_analysis

Revision ID: d4e5f6a1b2c3
Revises: c3d4e5f6a1b2
Create Date: 2026-10-23 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'd4e5f6a1b2c3'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a1b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create skill_gap_analyses table and add metadata columns to roles and role_requirements."""
    # 1. Update roles table
    op.add_column(
        'roles',
        sa.Column('version', sa.String(length=32), server_default='1.0.0', nullable=False),
    )
    op.add_column(
        'roles',
        sa.Column('source', sa.String(length=64), server_default='curated_baseline', nullable=False),
    )
    op.add_column(
        'roles',
        sa.Column('is_complete', sa.Boolean(), server_default=sa.text('TRUE'), nullable=False),
    )
    op.add_column(
        'roles',
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    # 2. Update role_requirements table
    op.add_column(
        'role_requirements',
        sa.Column('required_level', sa.Integer(), server_default='3', nullable=False),
    )
    op.add_column(
        'role_requirements',
        sa.Column('rationale', sa.Text(), nullable=True),
    )

    # 3. Create skill_gap_analyses table
    op.create_table(
        'skill_gap_analyses',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('career_profile_id', sa.Uuid(), nullable=False),
        sa.Column('role_id', sa.String(length=64), nullable=False),
        sa.Column('is_current', sa.Boolean(), server_default=sa.text('TRUE'), nullable=False),
        sa.Column('role_version', sa.String(length=32), server_default='1.0.0', nullable=False),
        sa.Column('algorithm_version', sa.String(length=32), server_default='1.0.0', nullable=False),
        sa.Column('role_alignment_score', sa.Numeric(precision=4, scale=1), nullable=False),
        sa.Column('evidence_coverage_score', sa.Numeric(precision=4, scale=1), nullable=False),
        sa.Column('status', sa.String(length=32), server_default='completed', nullable=False),
        sa.Column('strongest_skills', postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'), server_default=sa.text("'[]'"), nullable=False),
        sa.Column('developing_skills', postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'), server_default=sa.text("'[]'"), nullable=False),
        sa.Column('skill_gaps', postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'), server_default=sa.text("'[]'"), nullable=False),
        sa.Column('missing_skills', postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'), server_default=sa.text("'[]'"), nullable=False),
        sa.Column('unassessed_skills', postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'), server_default=sa.text("'[]'"), nullable=False),
        sa.Column('skill_details', postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'), server_default=sa.text("'{}'"), nullable=False),
        sa.Column('prioritized_gaps', postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'), server_default=sa.text("'[]'"), nullable=False),
        sa.Column('recommended_assessments', postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'), server_default=sa.text("'[]'"), nullable=False),
        sa.Column('explanation_narrative', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['career_profile_id'], ['career_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_index('skill_gap_analyses_profile_idx', 'skill_gap_analyses', ['career_profile_id'])
    op.create_index('skill_gap_analyses_profile_current_idx', 'skill_gap_analyses', ['career_profile_id', 'is_current'])
    op.create_index('skill_gap_analyses_role_idx', 'skill_gap_analyses', ['role_id'])


def downgrade() -> None:
    """Drop skill_gap_analyses table and remove added columns."""
    op.drop_index('skill_gap_analyses_role_idx', table_name='skill_gap_analyses')
    op.drop_index('skill_gap_analyses_profile_current_idx', table_name='skill_gap_analyses')
    op.drop_index('skill_gap_analyses_profile_idx', table_name='skill_gap_analyses')
    op.drop_table('skill_gap_analyses')

    op.drop_column('role_requirements', 'rationale')
    op.drop_column('role_requirements', 'required_level')

    op.drop_column('roles', 'updated_at')
    op.drop_column('roles', 'is_complete')
    op.drop_column('roles', 'source')
    op.drop_column('roles', 'version')
