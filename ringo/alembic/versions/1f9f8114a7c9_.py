"""Removed todo module

Revision ID: 1f9f8114a7c9
Revises: 28c50d6d4971
Create Date: 2015-01-31 14:15:54.104686

"""

# revision identifiers, used by Alembic.
revision = '1f9f8114a7c9'
down_revision = '28c50d6d4971'

from alembic import op


UPGRADE = """
DELETE FROM "actions" WHERE mid = 13;
DELETE FROM "modules" WHERE id = 13;
"""
DOWNGRADE = """"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    op.drop_table("nm_todo_users")
    op.drop_table("todos")
    iter_statements(UPGRADE)


def downgrade():
    iter_statements(DOWNGRADE)
