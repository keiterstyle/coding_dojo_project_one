"""empty message

Revision ID: 888e98c83a42
Revises: 
Create Date: 2020-03-17 18:44:27.660011

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '888e98c83a42'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.Column('belt_rank', sa.String(length=10), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('injuries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('injury_location', sa.String(length=55), nullable=True),
    sa.Column('injury_type', sa.String(length=55), nullable=True),
    sa.Column('pain_level', sa.String(length=55), nullable=True),
    sa.Column('pic', sa.String(length=55), nullable=True),
    sa.Column('injury_comment', sa.String(length=155), nullable=True),
    sa.Column('athlete_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['athlete_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('injuries')
    op.drop_table('users')
    # ### end Alembic commands ###
