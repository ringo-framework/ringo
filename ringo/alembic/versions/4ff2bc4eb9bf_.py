"""Removed nm_usergroup_roles table

Revision ID: 4ff2bc4eb9bf
Revises: 57c6ab33ad2f
Create Date: 2015-05-10 20:28:01.388673

"""

# revision identifiers, used by Alembic.
revision = '4ff2bc4eb9bf'
down_revision = '57c6ab33ad2f'

from alembic import op
import sqlalchemy as sa


UPGRADE = """"""
DOWNGRADE = """"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('nm_usergroup_roles')
    ### end Alembic commands ###
    iter_statements(UPGRADE)


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('nm_usergroup_roles',
    sa.Column('gid', sa.INTEGER(), nullable=True),
    sa.Column('rid', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['gid'], [u'usergroups.id'], ),
    sa.ForeignKeyConstraint(['rid'], [u'roles.id'], )
    )
    ### end Alembic commands ###
    iter_statements(DOWNGRADE)