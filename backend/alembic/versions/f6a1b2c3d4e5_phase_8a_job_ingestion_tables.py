"""phase_8a_job_ingestion_tables

Revision ID: f6a1b2c3d4e5
Revises: e5f6a1b2c3d4
Create Date: 2026-10-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'f6a1b2c3d4e5'
down_revision: Union[str, Sequence[str], None] = 'e5f6a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create job_sources, job_ingestion_runs, and enhance jobs/job_skills schema."""
    # 1. Create job_sources table
    op.create_table(
        'job_sources',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('provider_type', sa.String(length=32), nullable=False),
        sa.Column('base_url', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('TRUE'), nullable=False),
        sa.Column('rate_limit_per_minute', sa.Integer(), server_default='30', nullable=False),
        sa.Column('last_ingested_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('config_metadata', postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint(
            "provider_type IN ('seed', 'manual', 'api', 'mock')",
            name='job_sources_provider_type_check'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('job_sources_name_idx', 'job_sources', ['name'], unique=True)

    # 2. Create job_ingestion_runs table
    op.create_table(
        'job_ingestion_runs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('source_id', sa.Uuid(), nullable=True),
        sa.Column('source_name', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), server_default='pending', nullable=False),
        sa.Column('items_fetched', sa.Integer(), server_default='0', nullable=False),
        sa.Column('items_inserted', sa.Integer(), server_default='0', nullable=False),
        sa.Column('items_updated', sa.Integer(), server_default='0', nullable=False),
        sa.Column('items_skipped', sa.Integer(), server_default='0', nullable=False),
        sa.Column('items_errored', sa.Integer(), server_default='0', nullable=False),
        sa.Column('error_log', postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed', 'partial')",
            name='job_ingestion_runs_status_check'
        ),
        sa.ForeignKeyConstraint(['source_id'], ['job_sources.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('job_ingestion_runs_source_idx', 'job_ingestion_runs', ['source_name', 'started_at'], unique=False)

    # 3. Enhance jobs table
    op.add_column('jobs', sa.Column('source_url', sa.String(length=512), nullable=True))
    op.add_column('jobs', sa.Column('normalized_title', sa.String(length=255), nullable=True))
    op.add_column('jobs', sa.Column('normalized_location', sa.String(length=128), nullable=True))
    op.add_column('jobs', sa.Column('employment_type', sa.String(length=32), server_default='full_time', nullable=True))
    op.add_column('jobs', sa.Column('freshness_status', sa.String(length=32), server_default='active', nullable=False))
    op.add_column('jobs', sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('jobs', sa.Column('responsibilities', postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'), nullable=True))
    op.add_column('jobs', sa.Column('required_qualifications', postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'), nullable=True))
    op.add_column('jobs', sa.Column('preferred_qualifications', postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'), nullable=True))
    op.add_column('jobs', sa.Column('raw_source_payload', postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'), nullable=True))
    op.add_column('jobs', sa.Column('data_quality_score', sa.Numeric(precision=4, scale=2), nullable=True))

    op.create_check_constraint(
        'jobs_freshness_status_check',
        'jobs',
        "freshness_status IN ('active', 'needs_refresh', 'expired', 'closed')"
    )
    op.create_index('jobs_source_external_idx', 'jobs', ['source', 'external_id'], unique=False)
    op.create_index('jobs_freshness_idx', 'jobs', ['freshness_status', 'is_active'], unique=False)

    # 4. Enhance job_skills table
    op.add_column('job_skills', sa.Column('confidence_score', sa.Numeric(precision=4, scale=2), server_default='1.00', nullable=True))
    op.add_column('job_skills', sa.Column('source_phrase', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Revert Phase 8A schema extensions."""
    # 4. Revert job_skills
    op.drop_column('job_skills', 'source_phrase')
    op.drop_column('job_skills', 'confidence_score')

    # 3. Revert jobs
    op.drop_index('jobs_freshness_idx', table_name='jobs')
    op.drop_index('jobs_source_external_idx', table_name='jobs')
    op.drop_constraint('jobs_freshness_status_check', 'jobs', type_='check')
    op.drop_column('jobs', 'data_quality_score')
    op.drop_column('jobs', 'raw_source_payload')
    op.drop_column('jobs', 'preferred_qualifications')
    op.drop_column('jobs', 'required_qualifications')
    op.drop_column('jobs', 'responsibilities')
    op.drop_column('jobs', 'last_verified_at')
    op.drop_column('jobs', 'freshness_status')
    op.drop_column('jobs', 'employment_type')
    op.drop_column('jobs', 'normalized_location')
    op.drop_column('jobs', 'normalized_title')
    op.drop_column('jobs', 'source_url')

    # 2. Revert job_ingestion_runs
    op.drop_index('job_ingestion_runs_source_idx', table_name='job_ingestion_runs')
    op.drop_table('job_ingestion_runs')

    # 1. Revert job_sources
    op.drop_index('job_sources_name_idx', table_name='job_sources')
    op.drop_table('job_sources')
