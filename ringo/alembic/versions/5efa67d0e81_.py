"""Removed log module

Revision ID: 5efa67d0e81
Revises: 3f583d36e9d6
Create Date: 2015-02-01 00:07:19.303163

"""

# revision identifiers, used by Alembic.
revision = '5efa67d0e81'
down_revision = '3f583d36e9d6'

from alembic import op

UPGRADE = """
DELETE FROM "nm_action_roles" WHERE aid IN (SELECT id FROM actions WHERE mid = 10);
DELETE FROM "actions" WHERE mid = 10;
DELETE FROM "modules" WHERE id = 10;
"""
DOWNGRADE = """"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('nm_form_logs')
    op.drop_table('logs')
    ### end Alembic commands ###
    iter_statements(UPGRADE)


def downgrade():
    ### end Alembic commands ###
    iter_statements(DOWNGRADE)