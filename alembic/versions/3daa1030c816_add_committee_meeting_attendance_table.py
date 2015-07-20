"""add_committee_meeting_attendance_table

Revision ID: 3daa1030c816
Revises: 5647a4255cdc
Create Date: 2015-07-20 13:41:37.293770

"""

# revision identifiers, used by Alembic.
revision = '3daa1030c816'
down_revision = '5647a4255cdc'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('committee_meeting_attendance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('alternate_member', sa.Boolean(), nullable=True),
    sa.Column('chairperson', sa.Boolean(), nullable=False),
    sa.Column('meeting_id', sa.Integer(), nullable=False),
    sa.Column('member_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['meeting_id'], ['event.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['member_id'], ['member.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('event', sa.Column('actual_end_time', sa.Time(timezone=True), nullable=True))
    op.add_column('event', sa.Column('actual_start_time', sa.Time(timezone=True), nullable=True))
    op.add_column('event', sa.Column('pmg_monitor', sa.String(length=255), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('event', 'pmg_monitor')
    op.drop_column('event', 'actual_start_time')
    op.drop_column('event', 'actual_end_time')

    op.drop_table('committee_meeting_attendance')
    ### end Alembic commands ###
