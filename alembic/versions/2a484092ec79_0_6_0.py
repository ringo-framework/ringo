"""0.6.0

Revision ID: 2a484092ec79
Revises: 3c346dfc5edb
Create Date: 2013-08-19 22:51:49.746128

"""

INSERTS = """
insert into modules ("id", "name", "clazzpath", "label", "label_plural", "description", "str_repr", "display") values ('8', 'files', 'ringo.model.file.File', 'File', 'Files', NULL, NULL, 'header-menu');

"""

# revision identifiers, used by Alembic.
revision = '2a484092ec79'
down_revision = '3c346dfc5edb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute(INSERTS)
    pass


def downgrade():
    op.execute("DELETE from modules where id = 8")
