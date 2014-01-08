"""Add fields to form modul

Revision ID: 32154d55ffe7
Revises: 1b9688e1cc97
Create Date: 2013-12-05 15:15:36.642296

"""

# revision identifiers, used by Alembic.
revision = '32154d55ffe7'
down_revision = '1b9688e1cc97'

from alembic import op
import sqlalchemy as sa


INSERTS = """"""
DELETES = """"""


def iter_statements(stmts):
    for st in stmts.split('\n'):
        op.execute(st)


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('nm_form_logs',
    sa.Column('iid', sa.Integer(), nullable=True),
    sa.Column('lid', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['iid'], ['forms.id'], ),
    sa.ForeignKeyConstraint(['lid'], ['logs.id'], ),
    sa.PrimaryKeyConstraint()
    )
    op.add_column(u'forms', sa.Column('category', sa.Integer()))
    op.add_column(u'forms', sa.Column('created', sa.DateTime()))
    op.add_column(u'forms', sa.Column('definition', sa.Text()))
    op.add_column(u'forms', sa.Column('description', sa.Text()))
    op.add_column(u'forms', sa.Column('title', sa.String()))
    op.add_column(u'forms', sa.Column('updated', sa.DateTime()))
    ### end Alembic commands ###
    iter_statements(INSERTS)


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'forms', 'updated')
    op.drop_column(u'forms', 'title')
    op.drop_column(u'forms', 'description')
    op.drop_column(u'forms', 'definiton')
    op.drop_column(u'forms', 'created')
    op.drop_column(u'forms', 'category')
    op.drop_table('nm_form_logs')
    ### end Alembic commands ###
    iter_statements(DELETES)
