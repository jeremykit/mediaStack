"""add_category_id_to_live_sources

Revision ID: e2015490614d
Revises:
Create Date: 2026-01-26 22:11:49.595034

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2015490614d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create video_trim_tasks table if it doesn't exist
    op.create_table('video_trim_tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('video_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', name='trimstatus'), nullable=True),
    sa.Column('start_time', sa.Integer(), nullable=False),
    sa.Column('end_time', sa.Integer(), nullable=False),
    sa.Column('extract_audio', sa.Boolean(), nullable=True),
    sa.Column('keep_original', sa.Boolean(), nullable=True),
    sa.Column('audio_bitrate', sa.String(length=8), nullable=True),
    sa.Column('trimmed_video_path', sa.String(length=512), nullable=True),
    sa.Column('extracted_audio_path', sa.String(length=512), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['video_id'], ['video_files.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('video_trim_tasks', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_video_trim_tasks_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_video_trim_tasks_status'), ['status'], unique=False)
        batch_op.create_index('ix_video_trim_tasks_video_id', ['video_id'], unique=False)

    # Add new columns to live_sources table
    with op.batch_alter_table('live_sources', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('is_online', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('last_check_time', sa.DateTime(), nullable=True))
        batch_op.create_foreign_key('fk_live_sources_category_id', 'categories', ['category_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('live_sources', schema=None) as batch_op:
        batch_op.drop_constraint('fk_live_sources_category_id', type_='foreignkey')
        batch_op.drop_column('last_check_time')
        batch_op.drop_column('is_online')
        batch_op.drop_column('category_id')

    with op.batch_alter_table('video_trim_tasks', schema=None) as batch_op:
        batch_op.drop_index('ix_video_trim_tasks_video_id')
        batch_op.drop_index(batch_op.f('ix_video_trim_tasks_status'))
        batch_op.drop_index(batch_op.f('ix_video_trim_tasks_id'))

    op.drop_table('video_trim_tasks')
