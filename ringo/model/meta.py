from ringo.model import Base, sqlalchemy as sa


class MetaItem(Base):
    __tablename__ = 'meta'
    id = sa.Column(sa.Integer, primary_key=True)
    mid = sa.Column(sa.Integer)
    uid = sa.Column(sa.Integer)
    gid = sa.Column(sa.Integer)
    created = sa.Column(sa.Date)
    updated = sa.Column(sa.Date)

    # Configuration
    _table_fields = [('mid', 'MID'), ('uid', 'uid'), ('gid', 'GID')]

    def __unicode__(self):
        return str(self.id)


def init_model(dbsession):
    """Will setup the initial model for the usermanagement. This
    includes creating users, usergroups  roles and permissions.

    :dbsession: Database session to which the items will be added.
    :returns: None

    """
    pass
