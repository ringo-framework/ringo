import logging
import sqlalchemy as sa
from ringo.model import Base
from ringo.model.user import BaseItem
from ringo.lib.helpers import dynamic_import

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
    bundle = sa.Column(sa.Boolean, nullable=False,
                       server_default=sa.sql.expression.false())
    """Flag to indicate if the action should be available in the bundled
    actions"""
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
    gid = sa.Column(sa.Integer, sa.ForeignKey('usergroups.id'))

    default_group = sa.orm.relationship("Usergroup", uselist=False)
    actions = sa.orm.relationship("ActionItem",
                                  backref="modul",
                                  lazy="joined")

    _sql_eager_loads = ['actions.roles']

    def get_clazz(self):
        """Returns the clazz defined in the clazzpath attribute"""
        return dynamic_import(self.clazzpath)

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
        except:
            return ("%s", ["id"])
