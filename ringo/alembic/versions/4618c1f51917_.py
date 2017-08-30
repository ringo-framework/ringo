"""Make UUIDs NOT NULL

Revision ID: 4618c1f51917
Revises: 4b4d1358de99
Create Date: 2017-08-24 15:26:24.178891

"""

# revision identifiers, used by Alembic.
revision = '4618c1f51917'
down_revision = '4b4d1358de99'

import uuid
import sqlalchemy as sa
from alembic import op


def upgrade():
    conn = op.get_bind()
    metadata = sa.MetaData()
    modules = sa.Table('modules', metadata,
                       sa.Column('id', sa.Integer),
                       sa.Column('name', sa.String),
                       sa.Column('uuid', sa.String))
    for m_name in [row[1] for row in conn.execute(modules.select())]:
        # Add UUIDs where missing in all modules
        if m_name == 'modules':
            module = modules
        else:
            module = sa.Table(m_name, metadata,
                              sa.Column('id', sa.Integer),
                              sa.Column('uuid', sa.String))
        for item in conn.execute(module.select(module.c.uuid == None)):
            op.execute(module.update().where(
                module.c.id==item[0]).values(
                uuid=str(uuid.uuid4())))

        # Now we can make it mandatory:
        op.alter_column(m_name, 'uuid',
                        existing_type=sa.CHAR(length=36),
                        nullable=False)


def downgrade():
    conn = op.get_bind()
    metadata = sa.MetaData()
    modules = sa.Table('modules', metadata,
                       sa.Column('id', sa.Integer),
                       sa.Column('name', sa.String))
    for m_name in [row[1] for row in conn.execute(modules.select())]:
        op.alter_column(m_name, 'uuid',
                        existing_type=sa.CHAR(length=36),
                        nullable=True)
