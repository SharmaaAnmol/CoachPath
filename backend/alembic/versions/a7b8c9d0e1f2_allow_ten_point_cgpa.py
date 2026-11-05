"""allow 10-point CGPA on education.gpa

Revision ID: a7b8c9d0e1f2
Revises: d5e6f7a2b3c4
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a7b8c9d0e1f2'
down_revision: Union[str, Sequence[str], None] = 'd5e6f7a2b3c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('education_gpa_check', 'education', type_='check')
    op.alter_column('education', 'gpa', type_=sa.Numeric(4, 2), existing_nullable=True)
    op.create_check_constraint('education_gpa_check', 'education', 'gpa IS NULL OR (gpa >= 0.0 AND gpa <= 10.0)')


def downgrade() -> None:
    op.drop_constraint('education_gpa_check', 'education', type_='check')
    op.execute('UPDATE education SET gpa = NULL WHERE gpa > 4.0')
    op.alter_column('education', 'gpa', type_=sa.Numeric(3, 2), existing_nullable=True)
    op.create_check_constraint('education_gpa_check', 'education', 'gpa IS NULL OR (gpa >= 0.0 AND gpa <= 4.0)')
