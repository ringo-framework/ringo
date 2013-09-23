"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision}
Create Date: ${create_date}

"""

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

INSERTS = """"""
DELETES = """"""


def iter_statements(stmts):
    for st in stmts.split('\n'):
        op.execute(st)


def upgrade():
    ${upgrades if upgrades else "pass"}
    iter_statements(INSERTS)


def downgrade():
    ${downgrades if downgrades else "pass"}
    iter_statements(DELETES)
