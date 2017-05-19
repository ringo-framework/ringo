"""Add link action to modules

Revision ID: 4b4d1358de99
Revises: 13876647f64b
Create Date: 2017-04-24 12:21:50.554683

"""

# revision identifiers, used by Alembic.
revision = '4b4d1358de99'
down_revision = '13876647f64b'

import copy
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from ringo.model.modul import ModulItem, ActionItem, ACTIONS
from ringo.model.user import Role


INSERTS = """"""
DELETES = """DELETE FROM actions WHERE name = 'Link'"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    ## commands auto generated by Alembic - please adjust! ###
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('actions', sa.Column('admin', sa.Boolean(), server_default='0', nullable=False))

    connection = op.get_bind()
    aid = connection.execute("select max(id) from actions").fetchone()[0]
    SessionMaker = sessionmaker(bind=connection.engine)
    session = SessionMaker(bind=connection)
    modules = session.query(ModulItem).all()
    action = ACTIONS["link"]
    for m in modules:
        aid += 1
        new_action = copy.deepcopy(action)
        new_action.id = aid
        m.actions.append(new_action)
        session.flush()

    for m in modules:
        for action in m.actions:
            if action.name != "Read":
                continue
            # Role has READ permission. Now add Link
            for new_action in m.actions:
                if new_action.name == "Link":
                    for role in action.roles:
                        role.permissions.append(new_action)


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    connection = op.get_bind()
    SessionMaker = sessionmaker(bind=connection.engine)
    session = SessionMaker(bind=connection)
    result = session.query(ActionItem).filter(ActionItem.name == 'Link').all()
    for x in result:
        session.delete(x)
        session.flush()
    op.drop_column('actions', 'admin')