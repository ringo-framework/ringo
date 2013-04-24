import sqlalchemy as sa
from ringo.model import Base
from ringo.model.user import BaseItem
from ringo.lib.i18n import _

## NM-Table definitions
#nm_modules_actions = sa.Table(
#    'nm_modules_actions', Base.metadata,
#    sa.Column('mid', sa.Integer, sa.ForeignKey('modules.id')),
#    sa.Column('aid', sa.Integer, sa.ForeignKey('actions.id')),
#    sa.Column('required_permissio', sa.Text)
#)


class ActionItem(BaseItem, Base):
    __tablename__ = 'actions'
    _modul_id = 2
    id = sa.Column(sa.Integer, primary_key=True)
    mid = sa.Column(sa.Integer, sa.ForeignKey('modules.id'))
    name = sa.Column(sa.Text, nullable=False)
    url = sa.Column(sa.Text, nullable=False)
    icon = sa.Column(sa.Text, nullable=False)
    description = sa.Column(sa.Text)

    _table_fields = [('modul', 'Modul'), ('name', 'Name'), ('url', 'Url')]

    def __unicode__(self):
        return u"%s (%s/%s)" % (self.name, self.modul, self.url)


class ModulItem(BaseItem, Base):
    __tablename__ = 'modules'
    _modul_id = 1
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, unique=True, nullable=False)
    label = sa.Column(sa.Text, nullable=False)
    label_plural = sa.Column(sa.Text, nullable=False)
    description = sa.Column(sa.Text)
    str_repr = sa.Column(sa.Text)

    actions = sa.orm.relationship("ActionItem", backref="modul")

    _table_fields = [('name', 'Name')]

    def __unicode__(self):
        return self.name

    def get_label(self, plural=False):
        if plural:
            return self.label_plural
        return self.label


def _create_default_actions(dbsession):
    a0 = ActionItem(name="List", url="list", icon="icon-list-alt")
    a1 = ActionItem(name="Create", url="create", icon=" icon-plus")
    a2 = ActionItem(name="Read", url="read/{id}", icon="icon-eye-open")
    a3 = ActionItem(name="Update", url="update/{id}", icon="icon-edit")
    a4 = ActionItem(name="Delete", url="delete/{id}", icon="icon-trash")
    dbsession.add(a0)
    dbsession.add(a1)
    dbsession.add(a2)
    dbsession.add(a3)
    dbsession.add(a4)
    actions = [a0, a1, a2, a3, a4]
    return actions


def init_model(dbsession):
    """Will setup the initial model for the usermanagement. This
    includes creating users, usergroups  roles and permissions.

    :dbsession: Database session to which the items will be added.
    :returns: None

    """

    # ID 1
    modul = ModulItem(name='modules')
    modul.label = _("Modul")
    modul.label_plural = _("Modules")
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
    # ID 2
    modul = ModulItem(name='actions')
    modul.label = _("Action")
    modul.label_plural = _("Actions")
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
    # ID 3
    modul = ModulItem(name='users')
    modul.label = _("User")
    modul.label_plural = _("Users")
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
    # ID 4
    modul = ModulItem(name='usergroups')
    modul.label = _("Usergroup")
    modul.label_plural = _("Usergroups")
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
    # ID 5
    modul = ModulItem(name='roles')
    modul.label = _("Role")
    modul.label_plural = _("Roles")
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
    # ID 6
    modul = ModulItem(name='profiles')
    modul.label = _("Profile")
    modul.label_plural = _("Profiles")
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
