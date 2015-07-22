"""Added Owner and Group to roles, usergroups, users

Revision ID: 1a553ec2b34b
Revises: 3520cf26d8d8
Create Date: 2015-07-21 23:31:22.487231

"""

# revision identifiers, used by Alembic.
revision = '1a553ec2b34b'
down_revision = '3520cf26d8d8'

from alembic import op
import sqlalchemy as sa

UPGRADE = """
UPDATE roles set uid = 1;
UPDATE roles set gid = 1;
UPDATE usergroups set uid = 1;
UPDATE usergroups set gid = 1;
UPDATE users set uid = 1;
UPDATE users set gid = 1;
"""
DOWNGRADE = """"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("roles") as batch_op:
        batch_op.add_column(sa.Column('gid', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('uid', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_roles_gid_usergroups', 'usergroups', ['gid'], ['id'])
        batch_op.create_foreign_key('fk_roles_uid_usergroups', 'users', ['uid'], ['id'])

    with op.batch_alter_table("usergroups") as batch_op:
        batch_op.add_column(sa.Column('gid', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('uid', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_usergroups_gid_usergroups', 'usergroups', ['gid'], ['id'])
        batch_op.create_foreign_key('fk_usergroups_uid_users', 'users', ['uid'], ['id'])
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column('gid', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('uid', sa.Integer(), nullable=True))
        #  FIXME: Migration fails on SQLite when the following FK
        #  are enabled. As alembic in combination with sqlite does have
        #  many issues anyway we will disable the FK contrains for
        #  Sqlite (ti) <2015-07-22 09:17> 
        if batch_op.migration_context.dialect.name != 'sqlite':
            batch_op.create_foreign_key('fk_users_gid_usergroups', 'usergroups', ['gid'], ['id'])
            batch_op.create_foreign_key('fk_users_uid_users', 'users', ['uid'], ['id'])
    ### end Alembic commands ###
    iter_statements(UPGRADE)


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'uid')
    op.drop_column('users', 'gid')
    op.drop_column('usergroups', 'uid')
    op.drop_column('usergroups', 'gid')
    op.drop_column('roles', 'uid')
    op.drop_column('roles', 'gid')
    ### end Alembic commands ###
    iter_statements(DOWNGRADE)
