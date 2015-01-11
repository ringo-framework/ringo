"""Copy roles on groups to the user. Delete group roles.

Revision ID: 252cee80e23e
Revises: 5895338244f1
Create Date: 2014-04-29 10:10:02.172819

"""

# revision identifiers, used by Alembic.
revision = '252cee80e23e'
down_revision = '5895338244f1'

from alembic import op
import sqlalchemy as sa


INSERTS = """
INSERT INTO nm_user_roles (uid, rid) select g.uid, r.rid from nm_usergroup_roles r join nm_user_usergroups g on g.gid = r.gid;
DELETE FROM nm_usergroup_roles;
"""
DELETES = """"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    pass
    iter_statements(INSERTS)


def downgrade():
    pass
    iter_statements(DELETES)
