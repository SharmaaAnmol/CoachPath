"""phase_5a_resume_parsing_enhancements

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f6
Create Date: 2026-10-22 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a1'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add parsing failure tracking and timestamp columns to resumes table."""
    op.add_column('resumes', sa.Column('parsing_error', sa.Text(), nullable=True))
    op.add_column('resumes', sa.Column('parsing_error_category', sa.String(length=64), nullable=True))
    op.add_column('resumes', sa.Column('parsed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        'resumes',
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
    )

    # Update check constraint on PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.drop_constraint('resumes_status_check', 'resumes', type_='check')
        op.create_check_constraint(
            'resumes_status_check',
            'resumes',
            "status IN ('uploaded', 'parsing', 'processing', 'parsed', 'needs_review', 'failed')",
        )


def downgrade() -> None:
    """Revert resume parsing enhancement columns."""
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.drop_constraint('resumes_status_check', 'resumes', type_='check')
        op.create_check_constraint(
            'resumes_status_check',
            'resumes',
            "status IN ('uploaded', 'parsing', 'parsed', 'failed')",
        )

    op.drop_column('resumes', 'updated_at')
    op.drop_column('resumes', 'parsed_at')
    op.drop_column('resumes', 'parsing_error_category')
    op.drop_column('resumes', 'parsing_error')
