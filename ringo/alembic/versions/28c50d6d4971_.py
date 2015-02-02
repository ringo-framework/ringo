"""Remove Printtemplate module

Revision ID: 28c50d6d4971
Revises: 13822f7a643c
Create Date: 2015-01-31 12:49:58.945070

"""

# revision identifiers, used by Alembic.
revision = '28c50d6d4971'
down_revision = '13822f7a643c'

from alembic import op


UPGRADE = """
DELETE FROM "actions" WHERE mid = 15;
DELETE FROM "modules" WHERE id = 15;
"""
DOWNGRADE = """
"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    op.drop_table("printtemplates")
    iter_statements(UPGRADE)


def downgrade():
    iter_statements(DOWNGRADE)
