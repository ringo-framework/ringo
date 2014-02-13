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
    display = sa.Column(sa.Text, default="primary")
    """Optional. Configure where the action will be displayed. If display is
    'secondary' the action will be rendererd in the advanced dropdown
    context menu. Default is 'primary'"""
    permission = sa.Column(sa.Text)
    """Optional. Configure an alternative permission the user must have
    to be allowed to call this action. Known values are 'list', 'create',
    'read', 'update', 'delete', 'import', 'export'. If empty the
    permission system will use the the lowered name of the action."""

    def __unicode__(self):
        return u"%s (%s/%s)" % (self.name, self.modul, self.url)


ACTIONS = {
    "list":   ActionItem(name="List",
                         url="list",
                         icon="icon-list-alt"),
    "create": ActionItem(name="Create",
                         url="create",
                         icon=" icon-plus"),
    "read":   ActionItem(name="Read",
                         url="read/{id}",
                         icon="icon-eye-open"),
    "update": ActionItem(name="Update",
                         url="update/{id}",
                         icon="icon-edit"),
    "delete": ActionItem(name="Delete",
                         url="delete/{id}",
                         icon="icon-trash"),
    "import": ActionItem(name="Import",
                         url="import",
                         icon="icon-import"),
    "export": ActionItem(name="Export",
                         url="export/{id}",
                         icon="icon-export")
}


def configure_actions(modul, config, dbsession):
    new_actions = config.get("actions") or []
    old_actions = [action.name.lower() for action in modul.actions]
    delete_actions = (set(old_actions) - set(new_actions))
    add_actions = (set(new_actions) - set(old_actions))
    for name in delete_actions:
        log.info("Deleting action %s from modul %s" % (name, modul))
        action = modul.get_action(name)
        if action:
            modul.actions.remove(action)
    for name in add_actions:
        log.info("Adding action %s to modul %s" % (name, modul))
        action = ACTIONS.get(name)
        if action:
            modul.actions.append(action)
        else:
            log.error("Action %s is not known!" % (name))
    return modul


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

    actions = sa.orm.relationship("ActionItem",
                                  backref="modul",
                                  lazy="joined")

    _sql_eager_loads = ['actions.roles']

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

    def get_action(self, name):
        for action in self.actions:
            if action.name.lower() == name:
                return action
        return None

    def get_str_repr(self):
        """Return a tupel with format str and a list of fields."""
        # "%s - %s"|field1, field2 -> ("%s - %s", ["field1", "field2"])
        try:
            format_str, fields = self.str_repr.split("|")
            return (format_str, fields.split(","))
        except AttributeError:
            return ("%s", ["id"])


def load_modul(config, dbsession):
    name = config.get("name") + "s"
    try:
        return dbsession.query(ModulItem).filter(ModulItem.name == name).one()
    except sa.orm.exc.NoResultFound:
        return None


def add_modul(config, dbsession):

    # Set defaults
    name = config.get("name") + "s"
    clazzpath = config.get("clazzpath")
    str_repr = config.get("str_repr") or "%s|id"
    display = config.get("str_repr") or "hidden"
    label = config.get("label") or name
    label_plural = config.get("label_plural") or label

    # Add modul
    modul = ModulItem(name=name)
    modul.clazzpath = clazzpath
    modul.label = label
    modul.str_repr = str_repr
    modul.label_plural = label_plural
    modul.display = display
    dbsession.add(modul)
    dbsession.flush()
    log.info("Adding new modul '%s'" % modul)
    return modul


def register_modul(config, dbsession):
    """Will add a new modul entry including actions to the moduls table
    if the modul is not already present.

    :config: Dictionary with the modul configuration

    """
    # Add or load modul
    modul = load_modul(config, dbsession)
    if modul:
        log.debug("Modul %s already registered" % modul)
    else:
        modul = add_modul(config, dbsession)

    # Configure actions
    modul = configure_actions(modul, config, dbsession)

    return modul


def _create_default_actions(dbsession, ignore=[]):
    actions = []
    for key in ACTIONS:
        if not key in ignore:
            action = ACTIONS.get(key)
            actions.append(action)
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
    modul.actions.extend(_create_default_actions(dbsession,
                                                 ignore=['create', 'delete',
                                                         'import', 'export']))
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
    modul.actions.extend(_create_default_actions(dbsession,
                                                 ignore=['create', 'delete',
                                                         'import', 'export']))
    dbsession.add(modul)
