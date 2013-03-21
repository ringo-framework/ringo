import logging
from mako.lookup import TemplateLookup
from ringo import template_dir

template_lookup = TemplateLookup(directories=[template_dir],
                                 module_directory='/tmp/ringo_modules')

log = logging.getLogger(__name__)


class Renderer(object):
    """Baseclass for all renderers"""

    def __init__(self):
        """Initialize renderer"""
        pass

    def render(self):
        """Initialize renderer"""
        pass


class ListRenderer(Renderer):
    """Docstring for ListRenderer """

    def __init__(self, clazz):
        """@todo: to be defined """
        Renderer.__init__(self)
        self.clazz = clazz
        self.template = template_lookup.get_template("internal/list.mako")

    def render(self, items):
        """Initialize renderer"""
        values = {'items': items,
                  'headers': self.clazz._table_fields}
        return self.template.render(**values)
