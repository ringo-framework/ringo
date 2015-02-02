"""Removed news module

Revision ID: 4b9efcf216dc
Revises: 1f9f8114a7c9
Create Date: 2015-01-31 14:58:39.617403

"""

# revision identifiers, used by Alembic.
revision = '4b9efcf216dc'
down_revision = '1f9f8114a7c9'

from alembic import op


UPGRADE = """
DELETE FROM "nm_action_roles" WHERE aid IN (SELECT id FROM actions WHERE mid =9);
DELETE FROM "actions" WHERE mid = 9;
DELETE FROM "modules" WHERE id = 9;
"""
DOWNGRADE = """"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    op.drop_table("nm_news_user")
    op.drop_table("news")
    iter_statements(UPGRADE)


def downgrade():
    iter_statements(DOWNGRADE)
