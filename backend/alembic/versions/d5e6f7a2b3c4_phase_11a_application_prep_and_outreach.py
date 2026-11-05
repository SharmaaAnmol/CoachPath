"""phase_11a_application_prep_and_outreach

Revision ID: d5e6f7a2b3c4
Revises: c4d5e6f7a2b3
Create Date: 2026-10-31 13:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd5e6f7a2b3c4'
down_revision: Union[str, Sequence[str], None] = 'c4d5e6f7a2b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create application_packages and recruiter_outreach_drafts tables."""
    # 1. Create application_packages table
    op.create_table(
        'application_packages',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('job_id', sa.Uuid(), nullable=False),
        sa.Column('application_id', sa.Uuid(), nullable=True),
        sa.Column('source_resume_id', sa.Uuid(), nullable=False),
        sa.Column('tailored_resume_version_id', sa.Uuid(), nullable=False),
        sa.Column('status', sa.String(length=32), server_default=sa.text("'draft'"), nullable=False),
        sa.Column('cover_note', sa.Text(), nullable=False),
        sa.Column(
            'application_questions',
            postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column(
            'evidence_references',
            postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column(
            'generated_metadata',
            postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'),
            server_default=sa.text("'{}'"),
            nullable=False,
        ),
        sa.Column('user_notes', sa.Text(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('handoff_initiated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('application_url', sa.String(length=512), nullable=True),
        sa.Column('application_url_source', sa.String(length=64), nullable=True),
        sa.Column('user_confirmed_submission', sa.Boolean(), server_default=sa.text('FALSE'), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint(
            "status IN ('draft', 'edited', 'reviewed', 'approved', 'handoff_initiated', 'submitted')",
            name='application_packages_status_check',
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['source_resume_id'], ['resumes.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['tailored_resume_version_id'], ['resume_versions.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'idx_application_packages_user_status',
        'application_packages',
        ['user_id', 'status'],
        unique=False,
    )
    op.create_index(
        'idx_application_packages_job',
        'application_packages',
        ['job_id'],
        unique=False,
    )
    op.create_index(
        'idx_application_packages_tailored_version',
        'application_packages',
        ['tailored_resume_version_id'],
        unique=False,
    )

    # 2. Create recruiter_outreach_drafts table
    op.create_table(
        'recruiter_outreach_drafts',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('job_id', sa.Uuid(), nullable=False),
        sa.Column('application_package_id', sa.Uuid(), nullable=True),
        sa.Column('application_id', sa.Uuid(), nullable=True),
        sa.Column('recruiter_name', sa.String(length=128), nullable=True),
        sa.Column('recruiter_role_type', sa.String(length=128), nullable=True),
        sa.Column('recruiter_profile_url', sa.String(length=512), nullable=True),
        sa.Column('recruiter_contact_info', sa.String(length=255), nullable=True),
        sa.Column('candidate_notes', sa.Text(), nullable=True),
        sa.Column('subject_line', sa.String(length=255), nullable=False),
        sa.Column('message_body', sa.Text(), nullable=False),
        sa.Column('word_count', sa.Integer(), nullable=False),
        sa.Column(
            'suggested_role_types',
            postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
        sa.Column('status', sa.String(length=32), server_default=sa.text("'draft'"), nullable=False),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('handoff_initiated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('handoff_type', sa.String(length=32), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_confirmed_sent', sa.Boolean(), server_default=sa.text('FALSE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint(
            "status IN ('draft', 'awaiting_approval', 'approved', 'handoff_initiated', 'sent', 'cancelled')",
            name='recruiter_outreach_drafts_status_check',
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['application_package_id'], ['application_packages.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'idx_recruiter_outreach_user_status',
        'recruiter_outreach_drafts',
        ['user_id', 'status'],
        unique=False,
    )
    op.create_index(
        'idx_recruiter_outreach_package',
        'recruiter_outreach_drafts',
        ['application_package_id'],
        unique=False,
    )
    op.create_index(
        'idx_recruiter_outreach_job',
        'recruiter_outreach_drafts',
        ['job_id'],
        unique=False,
    )


def downgrade() -> None:
    """Drop recruiter_outreach_drafts and application_packages tables."""
    op.drop_index('idx_recruiter_outreach_job', table_name='recruiter_outreach_drafts')
    op.drop_index('idx_recruiter_outreach_package', table_name='recruiter_outreach_drafts')
    op.drop_index('idx_recruiter_outreach_user_status', table_name='recruiter_outreach_drafts')
    op.drop_table('recruiter_outreach_drafts')

    op.drop_index('idx_application_packages_tailored_version', table_name='application_packages')
    op.drop_index('idx_application_packages_job', table_name='application_packages')
    op.drop_index('idx_application_packages_user_status', table_name='application_packages')
    op.drop_table('application_packages')
