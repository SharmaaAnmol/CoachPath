"""step_3_assessment_option_randomization

Revision ID: c4d5e6f7a2b3
Revises: b3c4d5e6f7a2
Create Date: 2026-10-29 14:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c4d5e6f7a2b3'
down_revision: Union[str, Sequence[str], None] = 'b3c4d5e6f7a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add option_orders JSONB column to assessment_attempts for stable attempt-scoped option shuffling."""
    op.add_column(
        'assessment_attempts',
        sa.Column(
            'option_orders',
            postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'),
            server_default=sa.text("'{}'"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Drop option_orders column from assessment_attempts."""
    op.drop_column('assessment_attempts', 'option_orders')
