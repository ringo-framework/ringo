"""Insert export and import actions to profile module

Revision ID: 5895338244f1
Revises: c939303434c
Create Date: 2014-04-15 09:39:07.817955

"""

# revision identifiers, used by Alembic.
revision = '5895338244f1'
down_revision = 'c939303434c'

from alembic import op
import sqlalchemy as sa


INSERTS = """
INSERT INTO "actions" VALUES(104,6,'Export','export/{id}','icon-export',NULL,NULL,'primary',NULL,'1');
INSERT INTO "actions" VALUES(105,6,'Import','import','icon-import',NULL,NULL,'primary',NULL,'0');
"""
DELETES = """
DELETE from "actions" WHERE id = 105;
DELETE from "actions" WHERE id = 104;
"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    pass
    iter_statements(INSERTS)


def downgrade():
    pass
    iter_statements(DELETES)
