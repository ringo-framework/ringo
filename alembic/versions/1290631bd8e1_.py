"""Set string representation of ringo modules

Revision ID: 1290631bd8e1
Revises: 4d88e470c876
Create Date: 2014-05-02 10:45:52.606378

"""

# revision identifiers, used by Alembic.
revision = '1290631bd8e1'
down_revision = '4d88e470c876'

from alembic import op
import sqlalchemy as sa

# IDS
# 1 = Module
# 2 = Actions
# 3 = User
# 4 = Usergroup
# 5 = Role
# 6 = Profile
# 7 = Appointments
# 8 = File
# 9 = News
# 10 = Logs
# 11 = Comment
# 12 = Tags
# 13 = Todo
# 14 = Form
# 15 = Printtemplates

INSERTS = """
UPDATE modules set str_repr = '%s|name' where id = 1
UPDATE modules set str_repr = '%s (%s/%s)|name,modul,url' where id = 2
UPDATE modules set str_repr = '%s|login' where id = 3
UPDATE modules set str_repr = '%s|name' where id = 4
UPDATE modules set str_repr = '%s|name' where id = 5
UPDATE modules set str_repr = '%s %s|first_name,last_name' where id = 6
UPDATE modules set str_repr = '%s|title' where id = 7
UPDATE modules set str_repr = '%s (%s)|name,mime' where id = 8
UPDATE modules set str_repr = '%s|subject' where id = 9
UPDATE modules set str_repr = '%s|subject' where id = 10
UPDATE modules set str_repr = '%s|id' where id = 11
UPDATE modules set str_repr = '%s (%s)|name,modul' where id = 12
UPDATE modules set str_repr = '%s|name' where id = 13
UPDATE modules set str_repr = '%s|title' where id = 14
UPDATE modules set str_repr = '%s (%s)|name,modul' where id = 15
"""
DELETES = """
UPDATE modules set str_repr = '' where id = 1
UPDATE modules set str_repr = '' where id = 2
UPDATE modules set str_repr = '' where id = 3
UPDATE modules set str_repr = '' where id = 4
UPDATE modules set str_repr = '' where id = 5
UPDATE modules set str_repr = '' where id = 6
UPDATE modules set str_repr = '' where id = 7
UPDATE modules set str_repr = '' where id = 8
UPDATE modules set str_repr = '' where id = 9
UPDATE modules set str_repr = '' where id = 10
UPDATE modules set str_repr = '' where id = 11
UPDATE modules set str_repr = '' where id = 12
UPDATE modules set str_repr = '' where id = 13
UPDATE modules set str_repr = '' where id = 14
UPDATE modules set str_repr = '' where id = 15
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
