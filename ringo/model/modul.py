from ringo.model import Base, sqlalchemy as sa
from ringo.model.user import BaseItem

class Modul(BaseItem, Base):
    __tablename__ = 'modules'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, unique=True, nullable=False)
    label = sa.Column(sa.Text, nullable=False)
    label_plural = sa.Column(sa.Text, nullable=False)
    description = sa.Column(sa.Text)
    str_repr = sa.Column(sa.Text)

    # Relations
    #roles = sa.orm.relationship("Role",
    #                            secondary=nm_user_roles)
    #groups = sa.orm.relationship("Usergroup",
    #                             secondary=nm_user_usergroups,
    #                             backref='members')
    #default_group = sa.orm.relationship("Usergroup", uselist=False)

    # Configuration
    _table_fields = [('name', 'Name')]

    def __unicode__(self):
        return self.name

def init_model(dbsession):
    """Will setup the initial model for the usermanagement. This
    includes creating users, usergroups  roles and permissions.

    :dbsession: Database session to which the items will be added.
    :returns: None

    """
    modul = Modul(name='modules')
    modul.label = "Modul"
    modul.label_plural = "Modules"
    dbsession.add(modul)
    modul = Modul(name='users')
    modul.label = "User"
    modul.label_plural = "Users"
    dbsession.add(modul)
    modul = Modul(name='usergroups')
    modul.label = "Usergroup"
    modul.label_plural = "Usergroups"
    dbsession.add(modul)
    modul = Modul(name='roles')
    modul.label = "Role"
    modul.label_plural = "Roles"
    dbsession.add(modul)
    modul = Modul(name='permissions')
    modul.label = "Permission"
    modul.label_plural = "Permissions"
    dbsession.add(modul)
