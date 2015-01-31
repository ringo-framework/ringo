"""Removed appointment modul

Revision ID: 13822f7a643c
Revises: 46edfd16f379
Create Date: 2015-01-31 11:46:01.585169

"""

# revision identifiers, used by Alembic.
revision = '13822f7a643c'
down_revision = '46edfd16f379'

from alembic import op
import sqlalchemy as sa


UPGRADE = """
DELETE FROM "actions" WHERE mid = 7;
DELETE FROM "modules" WHERE id = 7;
"""
DOWNGRADE = """
"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    op.drop_table("appointments")
    iter_statements(UPGRADE)


def downgrade():
    iter_statements(DOWNGRADE)
