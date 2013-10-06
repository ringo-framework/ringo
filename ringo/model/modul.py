import logging
import sqlalchemy as sa
from ringo.model import Base
from ringo.model.user import BaseItem

log = logging.getLogger(__name__)


class ActionItem(BaseItem, Base):
    __tablename__ = 'actions'
    _modul_id = 2
    id = sa.Column(sa.Integer, primary_key=True)
    mid = sa.Column(sa.Integer, sa.ForeignKey('modules.id'))
    name = sa.Column(sa.Text, nullable=False)
    url = sa.Column(sa.Text, nullable=False)
    icon = sa.Column(sa.Text, nullable=False)
    description = sa.Column(sa.Text)

    def __unicode__(self):
        return u"%s (%s/%s)" % (self.name, self.modul, self.url)


class ModulItem(BaseItem, Base):
    __tablename__ = 'modules'
    _modul_id = 1
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Text, unique=True, nullable=False)
    clazzpath = sa.Column(sa.Text, unique=True, nullable=False)
    label = sa.Column(sa.Text, nullable=False)
    label_plural = sa.Column(sa.Text, nullable=False)
    description = sa.Column(sa.Text)
    str_repr = sa.Column(sa.Text)
    display = sa.Column(sa.Text)

    actions = sa.orm.relationship("ActionItem", backref="modul")

    _sql_joined_relations = ['actions']

    def __unicode__(self):
        return self.name

    def get_label(self, plural=False):
        if plural:
            return self.label_plural
        return self.label

    def has_action(self, url):
        """Will return True if the modul has a ActionItem configured
        with given url. Else false."""
        for action in self.actions:
            if action.url == url:
                return True
        return False

    def get_str_repr(self):
        """Return a tupel with format str and a list of fields."""
        # "%s - %s"|field1, field2 -> ("%s - %s", ["field1", "field2"])
        try:
            format_str, fields = self.str_repr.split("|")
            return (format_str, fields.split(","))
        except AttributeError:
            return ("%s", ["id"])


def _create_default_actions(dbsession, ignore=[]):
    # TODO: Translate the name of the Action (torsten) <2013-07-10 09:32>
    a0 = ActionItem(name="List", url="list", icon="icon-list-alt")
    a1 = ActionItem(name="Create", url="create", icon=" icon-plus")
    a2 = ActionItem(name="Read", url="read/{id}", icon="icon-eye-open")
    a3 = ActionItem(name="Update", url="update/{id}", icon="icon-edit")
    a4 = ActionItem(name="Delete", url="delete/{id}", icon="icon-trash")
    actions = []
    if not "list" in ignore:
        dbsession.add(a0)
        actions.append(a0)
    if not "create" in ignore:
        dbsession.add(a1)
        actions.append(a1)
    if not "read" in ignore:
        dbsession.add(a2)
        actions.append(a2)
    if not "update" in ignore:
        dbsession.add(a3)
        actions.append(a3)
    if not "delete" in ignore:
        dbsession.add(a4)
        actions.append(a4)
    return actions


def init_model(dbsession):
    """Will setup the initial model for the usermanagement. This
    includes creating users, usergroups  roles and permissions.

    :dbsession: Database session to which the items will be added.
    :returns: None

    """

    # ID 1
    modul = ModulItem(name='modules')
    modul.clazzpath = "ringo.model.modul.ModulItem"
    modul.label = "Modul"
    modul.label_plural = "Modules"
    modul.display = "admin-menu"
    modul.actions.extend(_create_default_actions(dbsession, ignore=['create', 'delete']))
    dbsession.add(modul)
    # ID 2
    modul = ModulItem(name='actions')
    modul.clazzpath = "ringo.model.modul.ActionItem"
    modul.label = "Action"
    modul.label_plural = "Actions"
    modul.display = "admin-menu"
    # Actions modul is not meant to be callable from anybody (There is
    # now view at all). So do not add any actions here.
    # modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
    # ID 3
    modul = ModulItem(name='users')
    modul.clazzpath = "ringo.model.user.User"
    modul.display = "admin-menu"
    modul.label = "User"
    modul.label_plural = "Users"
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
    # ID 4
    modul = ModulItem(name='usergroups')
    modul.clazzpath = "ringo.model.user.Usergroup"
    modul.label = "Usergroup"
    modul.label_plural = "Usergroups"
    modul.display = "admin-menu"
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
    # ID 5
    modul = ModulItem(name='roles')
    modul.clazzpath = "ringo.model.user.Role"
    modul.label = "Role"
    modul.label_plural = "Roles"
    modul.display = "admin-menu"
    modul.actions.extend(_create_default_actions(dbsession))
    dbsession.add(modul)
    # ID 6
    modul = ModulItem(name='profiles')
    modul.clazzpath = "ringo.model.user.Profile"
    modul.label = "Profile"
    modul.label_plural = "Profiles"
    modul.display = "admin-menu"
    modul.actions.extend(_create_default_actions(dbsession, ignore=['create', 'delete']))
    dbsession.add(modul)
