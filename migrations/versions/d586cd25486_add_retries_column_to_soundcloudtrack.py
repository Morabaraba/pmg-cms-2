"""Add retries column to SoundcloudTrack

Revision ID: d586cd25486
Revises: 29918969a90
Create Date: 2016-09-09 13:36:57.354460

"""

# revision identifiers, used by Alembic.
revision = 'd586cd25486'
down_revision = '29918969a90'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('soundcloud_track', sa.Column('retries', sa.Integer(), nullable=True))
    op.execute('update soundcloud_track set retries = 0')
    op.alter_column('soundcloud_track', 'retries', nullable=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('soundcloud_track', 'retries')
    ### end Alembic commands ###
