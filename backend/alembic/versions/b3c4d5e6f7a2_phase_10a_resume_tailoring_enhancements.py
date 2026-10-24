"""phase_10a_resume_tailoring_enhancements

Revision ID: b3c4d5e6f7a2
Revises: a2b3c4d5e6f7
Create Date: 2026-10-24 23:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b3c4d5e6f7a2'
down_revision: Union[str, Sequence[str], None] = 'a2b3c4d5e6f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Enhance resume_versions schema with direct user ownership and modification timestamps."""
    # 1. Add user_id column (initially nullable for backfill safety)
    op.add_column(
        'resume_versions',
        sa.Column(
            'user_id',
            sa.Uuid(),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=True,
        )
    )

    # 2. Backfill user_id from parent resume if any records exist
    op.execute(
        sa.text(
            "UPDATE resume_versions SET user_id = resumes.user_id "
            "FROM resumes WHERE resume_versions.resume_id = resumes.id"
        )
    )

    # 3. Add updated_at timestamp column
    op.add_column(
        'resume_versions',
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        )
    )

    # 4. Create user_id index for fast candidate version lookups
    op.create_index(
        'resume_versions_user_id_idx',
        'resume_versions',
        ['user_id'],
        unique=False,
    )


def downgrade() -> None:
    """Revert resume_versions tailoring enhancements."""
    op.drop_index('resume_versions_user_id_idx', table_name='resume_versions')
    op.drop_column('resume_versions', 'updated_at')
    op.drop_column('resume_versions', 'user_id')
