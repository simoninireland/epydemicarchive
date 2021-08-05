"""Initial models

Revision ID: af4c5eff0608
Revises: 
Create Date: 2021-08-05 16:49:30.214573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'af4c5eff0608'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tag_name'), 'tag', ['name'], unique=False)
    op.create_table('topology',
    sa.Column('id', sa.String(length=128), nullable=False),
    sa.Column('N', sa.Integer(), nullable=True),
    sa.Column('M', sa.Integer(), nullable=True),
    sa.Column('kmean', sa.Float(), nullable=True),
    sa.Column('kmedian', sa.Float(), nullable=True),
    sa.Column('kvariance', sa.Float(), nullable=True),
    sa.Column('kmax', sa.Integer(), nullable=True),
    sa.Column('kmin', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('api_key', sa.String(length=128), nullable=True),
    sa.Column('api_key_expires', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_api_key'), 'user', ['api_key'], unique=False)
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_table('network',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('filename', sa.String(length=256), nullable=True),
    sa.Column('uploaded', sa.DateTime(), nullable=True),
    sa.Column('available', sa.Boolean(), nullable=True),
    sa.Column('title', sa.String(length=256), nullable=True),
    sa.Column('description', sa.String(length=1024), nullable=True),
    sa.Column('user_id', sa.String(length=128), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('profile',
    sa.Column('user_id', sa.String(length=128), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('affiliation', sa.String(length=128), nullable=True),
    sa.Column('url', sa.String(length=128), nullable=True),
    sa.Column('bio', sa.String(length=2048), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('tags',
    sa.Column('network', sa.String(length=64), nullable=False),
    sa.Column('tag', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['network'], ['network.id'], ),
    sa.ForeignKeyConstraint(['tag'], ['tag.id'], ),
    sa.PrimaryKeyConstraint('network', 'tag')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tags')
    op.drop_table('profile')
    op.drop_table('network')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_index(op.f('ix_user_api_key'), table_name='user')
    op.drop_table('user')
    op.drop_table('topology')
    op.drop_index(op.f('ix_tag_name'), table_name='tag')
    op.drop_table('tag')
    # ### end Alembic commands ###
