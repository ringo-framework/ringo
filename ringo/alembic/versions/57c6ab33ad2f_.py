"""Added label attribute to roles module

Revision ID: 57c6ab33ad2f
Revises: 5efa67d0e81
Create Date: 2015-02-04 16:13:04.358376

"""

# revision identifiers, used by Alembic.
revision = '57c6ab33ad2f'
down_revision = '5efa67d0e81'

from alembic import op
import sqlalchemy as sa


UPGRADE = """"""
DOWNGRADE = """"""


def iter_statements(stmts):
    for st in [x for x in stmts.split('\n') if x]:
        op.execute(st)


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('roles', sa.Column('label', sa.Text(), server_default='', nullable=False))
    ### end Alembic commands ###
    iter_statements(UPGRADE)


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('roles', 'label')
    ### end Alembic commands ###
    iter_statements(DOWNGRADE)