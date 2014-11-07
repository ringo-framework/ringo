"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision}
Create Date: ${create_date}

"""

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}

from alembic import op
from alembic_sqlite.op import drop_column_sqlite
import sqlalchemy as sa
${imports if imports else ""}

drop_column_default = op.drop_column
def drop_column(tablename, columnname):
    if op.get_context().dialect.name == 'sqlite':
        drop_column_sqlite(tablename, [columnname])
    else:
        drop_column_default(tablename, columnname)
op.drop_column = drop_column

INSERTS = """"""
DELETES = """"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    ${upgrades if upgrades else "pass"}
    iter_statements(INSERTS)


def downgrade():
    ${downgrades if downgrades else "pass"}
    iter_statements(DELETES)
