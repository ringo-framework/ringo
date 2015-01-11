"""Add import and export actions

Revision ID: 567ddf0f6079
Revises: 3bc33da5cbd2
Create Date: 2014-01-06 19:37:25.882521

"""

# revision identifiers, used by Alembic.
revision = '567ddf0f6079'
down_revision = '3bc33da5cbd2'

from alembic import op
import sqlalchemy as sa


INSERTS = """"""
DELETES = """
DELETE FROM actions where name = 'Import'
DELETE FROM actions where name = 'Export'
"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    conn = op.get_bind()
    res = conn.execute("select * from modules")
    max_action_id = conn.execute("select max(id) from actions").fetchone()[0]
    results = res.fetchall()
    for r in results:
        if r.name in ['modules', 'profiles']: continue
        max_action_id += 1
        stmnt = "INSERT into actions (id, mid, name, url, icon) VALUES (%s, %s, 'Export', 'export/{id}', 'icon-export')" % (max_action_id, r[0])
        op.execute(stmnt)
        max_action_id += 1
        stmnt = "INSERT into actions (id, mid, name, url, icon) VALUES (%s, %s, 'Import', 'import', 'icon-import')" % (max_action_id, r[0])
        op.execute(stmnt)
    iter_statements(INSERTS)


def downgrade():
    pass
    iter_statements(DELETES)
