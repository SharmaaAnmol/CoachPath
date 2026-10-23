"""phase_7a_roadmap_enhancements

Revision ID: e5f6a1b2c3d4
Revises: d4e5f6a1b2c3
Create Date: 2026-10-23 17:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'e5f6a1b2c3d4'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a1b2c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Phase 7A roadmap curriculum, tracking, and scheduling columns."""
    # 1. Roadmaps table enhancements
    op.add_column(
        'roadmaps',
        sa.Column('skill_gap_analysis_id', sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        'fk_roadmaps_gap_analysis_id',
        'roadmaps',
        'skill_gap_analyses',
        ['skill_gap_analysis_id'],
        ['id'],
        ondelete='SET NULL',
    )
    op.create_index('roadmaps_gap_analysis_idx', 'roadmaps', ['skill_gap_analysis_id'], unique=False)
    op.add_column(
        'roadmaps',
        sa.Column('description', sa.Text(), nullable=True),
    )
    op.add_column(
        'roadmaps',
        sa.Column('status', sa.String(length=32), server_default='active', nullable=False),
    )
    op.add_column(
        'roadmaps',
        sa.Column('generation_mode', sa.String(length=32), server_default='deterministic_ai', nullable=False),
    )
    op.add_column(
        'roadmaps',
        sa.Column('weekly_hours', sa.Integer(), server_default='10', nullable=False),
    )
    op.add_column(
        'roadmaps',
        sa.Column('total_estimated_hours', sa.Integer(), server_default='0', nullable=False),
    )
    op.add_column(
        'roadmaps',
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        'roadmaps',
        sa.Column('target_completion_date', sa.DateTime(timezone=True), nullable=True),
    )

    # 2. Roadmap Phases table enhancements
    op.add_column(
        'roadmap_phases',
        sa.Column('objective', sa.Text(), nullable=True),
    )
    op.add_column(
        'roadmap_phases',
        sa.Column('estimated_hours', sa.Integer(), server_default='0', nullable=False),
    )
    op.add_column(
        'roadmap_phases',
        sa.Column('prerequisites', sa.Text(), nullable=True),
    )
    op.add_column(
        'roadmap_phases',
        sa.Column('completion_criteria', sa.Text(), nullable=True),
    )
    op.add_column(
        'roadmap_phases',
        sa.Column('status', sa.String(length=32), server_default='pending', nullable=False),
    )

    # 3. Roadmap Tasks table enhancements
    op.add_column(
        'roadmap_tasks',
        sa.Column('learning_objective', sa.Text(), nullable=True),
    )
    op.add_column(
        'roadmap_tasks',
        sa.Column('task_type', sa.String(length=32), server_default='project', nullable=False),
    )
    op.add_column(
        'roadmap_tasks',
        sa.Column('priority', sa.String(length=16), server_default='medium', nullable=False),
    )
    op.add_column(
        'roadmap_tasks',
        sa.Column(
            'prerequisite_task_ids',
            postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), 'sqlite'),
            server_default=sa.text("'[]'"),
            nullable=False,
        ),
    )
    op.add_column(
        'roadmap_tasks',
        sa.Column('completion_criteria', sa.Text(), nullable=True),
    )
    op.add_column(
        'roadmap_tasks',
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        'roadmap_tasks',
        sa.Column('source_gap_priority', sa.String(length=32), nullable=True),
    )
    op.create_index('roadmap_tasks_skill_idx', 'roadmap_tasks', ['skill_id'], unique=False)


def downgrade() -> None:
    """Revert Phase 7A columns."""
    op.drop_index('roadmap_tasks_skill_idx', table_name='roadmap_tasks')
    op.drop_column('roadmap_tasks', 'source_gap_priority')
    op.drop_column('roadmap_tasks', 'due_date')
    op.drop_column('roadmap_tasks', 'completion_criteria')
    op.drop_column('roadmap_tasks', 'prerequisite_task_ids')
    op.drop_column('roadmap_tasks', 'priority')
    op.drop_column('roadmap_tasks', 'task_type')
    op.drop_column('roadmap_tasks', 'learning_objective')

    op.drop_column('roadmap_phases', 'status')
    op.drop_column('roadmap_phases', 'completion_criteria')
    op.drop_column('roadmap_phases', 'prerequisites')
    op.drop_column('roadmap_phases', 'estimated_hours')
    op.drop_column('roadmap_phases', 'objective')

    op.drop_index('roadmaps_gap_analysis_idx', table_name='roadmaps')
    op.drop_constraint('fk_roadmaps_gap_analysis_id', 'roadmaps', type_='foreignkey')
    op.drop_column('roadmaps', 'target_completion_date')
    op.drop_column('roadmaps', 'start_date')
    op.drop_column('roadmaps', 'total_estimated_hours')
    op.drop_column('roadmaps', 'weekly_hours')
    op.drop_column('roadmaps', 'generation_mode')
    op.drop_column('roadmaps', 'status')
    op.drop_column('roadmaps', 'description')
    op.drop_column('roadmaps', 'skill_gap_analysis_id')
