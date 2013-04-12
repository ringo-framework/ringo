import sqlalchemy as sa
from ringo.model import Base
from ringo.model.user import BaseItem
from ringo.lib.i18n import _


class ModulItem(BaseItem, Base):
    __tablename__ = 'modules'
    _modul_id = 1
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, unique=True, nullable=False)
    label = sa.Column(sa.Text, nullable=False)
    label_plural = sa.Column(sa.Text, nullable=False)
    description = sa.Column(sa.Text)
    str_repr = sa.Column(sa.Text)

    _table_fields = [('name', 'Name')]

    def __unicode__(self):
        return self.name

    def get_label(self, plural=False):
        if plural:
            return self.label_plural
        return self.label


def init_model(dbsession):
    """Will setup the initial model for the usermanagement. This
    includes creating users, usergroups  roles and permissions.

    :dbsession: Database session to which the items will be added.
    :returns: None

    """
    modul = ModulItem(name='modules')
    modul.label = _("Modul")
    modul.label_plural = _("Modules")
    modul = ModulItem(name='users')
    modul.label = _("User")
    modul.label_plural = _("Users")
    dbsession.add(modul)
    modul = ModulItem(name='usergroups')
    modul.label = _("Usergroup")
    modul.label_plural = _("Usergroups")
    dbsession.add(modul)
    modul = ModulItem(name='roles')
    modul.label = _("Role")
    modul.label_plural = _("Roles")
    dbsession.add(modul)
    modul = ModulItem(name='permissions')
    modul.label = _("Permission")
    modul.label_plural = _("Permissions")
    dbsession.add(modul)
    modul = ModulItem(name='profiles')
    modul.label = _("Profile")
    modul.label_plural = _("Profiles")
    dbsession.add(modul)
