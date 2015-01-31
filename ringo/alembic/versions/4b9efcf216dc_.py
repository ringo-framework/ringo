"""Removed news module

Revision ID: 4b9efcf216dc
Revises: 46edfd16f379
Create Date: 2015-01-31 14:58:39.617403

"""

# revision identifiers, used by Alembic.
revision = '4b9efcf216dc'
down_revision = '46edfd16f379'

from alembic import op


UPGRADE = """
DELETE FROM "actions" WHERE mid = 9;
DELETE FROM "modules" WHERE id = 9;
"""
DOWNGRADE = """"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    pass
    iter_statements(UPGRADE)


def downgrade():
    pass
    iter_statements(DOWNGRADE)
