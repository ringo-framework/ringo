"""Removed not null constraint on uuid

Revision ID: 99fda072ff9
Revises: 1a553ec2b34b
Create Date: 2015-09-05 20:05:31.083712

"""

# revision identifiers, used by Alembic.
revision = '99fda072ff9'
down_revision = '1a553ec2b34b'

from alembic import op
import sqlalchemy as sa


UPGRADE = """"""
DOWNGRADE = """"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('actions', 'uuid',
               existing_type=sa.CHAR(length=32),
               nullable=True)
    op.alter_column('forms', 'uuid',
               existing_type=sa.CHAR(length=32),
               nullable=True)
    op.alter_column('modules', 'uuid',
               existing_type=sa.CHAR(length=32),
               nullable=True)
    op.alter_column('profiles', 'uuid',
               existing_type=sa.CHAR(length=32),
               nullable=True)
    op.alter_column('roles', 'uuid',
               existing_type=sa.CHAR(length=32),
               nullable=True)
    op.alter_column('usergroups', 'uuid',
               existing_type=sa.CHAR(length=32),
               nullable=True)
    op.alter_column('users', 'uuid',
               existing_type=sa.CHAR(length=32),
               nullable=True)
    ### end Alembic commands ###
    iter_statements(UPGRADE)


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'uuid',
               existing_type=sa.CHAR(length=32),
               nullable=False)
    op.alter_column('usergroups', 'uuid',
               existing_type=sa.CHAR(length=32),
               nullable=False)
    op.alter_column('roles', 'uuid',
               existing_type=sa.CHAR(length=32),
               nullable=False)
    op.alter_column('profiles', 'uuid',
               existing_type=sa.CHAR(length=32),
               nullable=False)
    op.alter_column('modules', 'uuid',
               existing_type=sa.CHAR(length=32),
               nullable=False)
    op.alter_column('forms', 'uuid',
               existing_type=sa.CHAR(length=32),
               nullable=False)
    op.alter_column('actions', 'uuid',
               existing_type=sa.CHAR(length=32),
               nullable=False)
    ### end Alembic commands ###
    iter_statements(DOWNGRADE)
