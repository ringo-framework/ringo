"""Add uuid field

Revision ID: 3bc33da5cbd2
Revises: 28f748937454
Create Date: 2014-01-06 18:48:20.306078

"""

# revision identifiers, used by Alembic.
revision = '3bc33da5cbd2'
down_revision = '28f748937454'

from alembic import op
import sqlalchemy as sa


INSERTS = """"""
DELETES = """"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('actions', sa.Column('uuid', sa.CHAR(length=32)))
    op.add_column('appointments', sa.Column('uuid', sa.CHAR(length=32)))
    op.add_column('comments', sa.Column('uuid', sa.CHAR(length=32)))
    op.add_column('files', sa.Column('uuid', sa.CHAR(length=32)))
    op.add_column('logs', sa.Column('uuid', sa.CHAR(length=32)))
    op.add_column('modules', sa.Column('uuid', sa.CHAR(length=32)))
    op.add_column('news', sa.Column('uuid', sa.CHAR(length=32)))
    op.add_column('profiles', sa.Column('uuid', sa.CHAR(length=32)))
    op.add_column('roles', sa.Column('uuid', sa.CHAR(length=32)))
    op.add_column('tags', sa.Column('uuid', sa.CHAR(length=32)))
    op.add_column('todos', sa.Column('uuid', sa.CHAR(length=32)))
    op.add_column('usergroups', sa.Column('uuid', sa.CHAR(length=32)))
    op.add_column('users', sa.Column('uuid', sa.CHAR(length=32)))
    ### end Alembic commands ###
    iter_statements(INSERTS)


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'uuid')
    op.drop_column('usergroups', 'uuid')
    op.drop_column('todos', 'uuid')
    op.drop_column('tags', 'uuid')
    op.drop_column('roles', 'uuid')
    op.drop_column('profiles', 'uuid')
    op.drop_column('news', 'uuid')
    op.drop_column('modules', 'uuid')
    op.drop_column('logs', 'uuid')
    op.drop_column('files', 'uuid')
    op.drop_column('comments', 'uuid')
    op.drop_column('appointments', 'uuid')
    op.drop_column('actions', 'uuid')
    ### end Alembic commands ###
    iter_statements(DELETES)
