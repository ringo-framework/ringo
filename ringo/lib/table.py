"""Modul to with function to work with the table configuration"""
import logging
import os
import json
from ringo.lib.helpers import get_path_to, get_app_inheritance_path
from ringo.lib.cache import CACHE_TABLE_CONFIG

log = logging.getLogger(__name__)


def get_table_config(clazz, tablename=None):
    """Returns the table (overview, listing) configuration with the
    name 'tablename' of this Item from the configuration file. If
    the default table configuration will be returned. The table
    configuration is cached for later requests.

    :clazz: @todo
    :tablename: @todo
    :returns: @todo

    """
    # As this is a class method of the BaseItem we need to build a
    # unique cachename for tableconfigs among all inherited classes.
    cachename = "%s.%s" % (clazz.__name__, tablename)
    if not CACHE_TABLE_CONFIG.get(cachename):
        CACHE_TABLE_CONFIG.set(cachename, TableConfig(clazz, tablename))
    return CACHE_TABLE_CONFIG.get(cachename)


def get_path_to_overview_config(filename, app=None, location=None):
    """Returns the path the the given overview configuration. The file name
    should be realtive to the default location for the configurations.

    :file: filename
    :returns: Absolute path to the configuration file

    """
    if location is None:
        location = "views/tables"
    return get_path_to(os.path.join(location, filename), app)


class TableConfig:
    """The TableConfig clazz provides an interface for configuring the
    overview of the the given clazz. The configuration includes

    * Enabled features of the overview
    * Which fields should be enabled in the overview
    * Labeling of the fields
    * Rendering of the fields
    * Layout of the table (column width etc.)

    The configuration of the overview is loaded from a an JSON
    configuration file which is located under view/overviews relative to
    the application root.

    The configuration has the following form and options::

        {
            "overview": {
                "columns": [
                    {
                        "name": "fieldname",
                        "label": "Label",
                        "width": "width",
                        "screen": "xlarge",
                        "expand": true,
                        "filter": false,
                        "title": "Tooltip title"
                    }
                ]
                "settings": {
                    "default-sort-field": "name",
                    "default-sort-order": "desc",
                    "auto-responsive": true,
                    "advancedsearch": true
                },
                "filters": [
                    {
                        "field": "fieldname",
                        "type": "checkbox",
                        "expr": "",
                        "regex": false,
                        "smart": true,
                        "caseinsensitive": true
                    }
                ]
            }
        }

    The configuration can have configurations for more than one table
    configuration. The default name of a configuration is *overview*.
    The next sections defines the *columns* of the table. The columns
    are rendered in the order they are defined. Each column can have the
    following options:

    * *name*: The name of the attribute within clazz which should be
      listed here.
    * *label*: The label of the field.
    * *width*: The width of the field. If not units are given the pixel
      are assumed.
    * *screen*: Define from which size on this field will be displayed.
      Defaults to "small" which means rendering on all sizes.
      Available media sizes: (xlarge, large, medium, small).
    * *expand*: The expand option is used to expand the referneces
      values in selections into the literal value of the corrispondig
      option. Note that this option is only usefull for selection fields
      in *formbar* which do not have a real relation attached. In all
      other cases the reference values are expanded automatically.
    * *filter*: The filter determines if the rendered link is a filter
      link. A filter link is a shortcut to trigger a search with the
      current value of the field in the current column over all items.
      Defaults to No.
    * *title* A tooltip will be rendered for the table header of the
      column.

    Further the table has some table wide configuration options:

    * *sortable*: If True, the table is sortable.
    * *default-sort-field*: Name of the column which should be used as
      default sorting on the table. Defaults to the first column in the table.
    * *default-sort-order*: Sort order (desc, asc) Defaults to asc.

    * *searchable*: If True, the table is searchable and a search field is
      shown.
    * *default-search*: Default search filter for the table
    * *advancedsearch*: If False, a more complex overview with stacked
      search regex and save features is used. Otherwise a more simple
      overview. Default to use the simple overview.

    * *pagination*: If True pagination of the results will be enabled.
      The table will have gui element to configure pagination of the
      table. Defaults to false.

    * *auto-responsive*: If True than only the first column of a table
      will be displayed on small devices. Else you need to configure the
      "screen" attribute for the fields.
    * *show-info*: It True than a info field showing number of items in the 
      table

    For DT tables you can define different search filters which are
    defined in the *filters* section. Filters is a list of different
    filter options. Each filter has the following options:

    * *field*: The name of the field on which the filter will be applied.
    * *label*: The label of the filter.
    * *active*: If true the filter will be active.
    * *type*: Type of the rendering. Currently only "checkbox" is
      supported. The checkbox renderer will active or deactive a filter
      a a certain row.
    * *expr*: The expression for the filter.
    * *smart*: If set to True this filter is a smart filter. Defaults to True.
    * *regex*: If set to True this the expression is handled as a
      regular expression. Defaults to False.
    * *caseinsensitive*: If set to True the search is caseinsensitive.
      Defaults to True.


    """

    def __init__(self, clazz, name):
        """Will initialize the configuration of the overview for the
        clazz.

        :clazz: The clazz for which the overview configuration should be
        loaded.
        :name: name of the configuration. Defaults to the
        "overview" configuration.
        """
        self.clazz = clazz
        self.name = name or "overview"
        self.config = _load_overview_config(clazz)

    def get_settings(self):
        """Returns the settings for the table as dictionary
        :returns: Settings dictionary

        """
        config = self.config.get(self.name)
        return config.get('settings', {})

    def get_filters(self):
        """Returns the filters for the table as dictionary
        :returns: Filters dictionary

        """
        config = self.config.get(self.name)
        return [Filter(fltr) for fltr in config.get('filters', [])]

    def is_autoresponsive(self):
        settings = self.get_settings()
        return settings.get("auto-responsive", True)

    def is_sortable(self):
        settings = self.get_settings()
        return settings.get("sortable", True)

    def is_searchable(self):
        settings = self.get_settings()
        return settings.get("searchable", True)

    def is_paginated(self):
        settings = self.get_settings()
        return settings.get("pagination", False)

    def is_advancedsearch(self, default=False):
        settings = self.get_settings()
        return settings.get("advancedsearch", default)

    def get_columns(self):
        """Return a list of configured columns within the configuration.
        Each colum is a dictionary containing the one or more available
        conifguration attributes."""
        cols = []
        config = self.config.get(self.name)
        for col in config.get('columns'):
            cols.append(col)
        return cols

    def get_column_index(self, name):
        """Will return the index of the column in the overview. Index is
        count from left to right. This method is used to match the
        configured columns in this configuration with the columns in the
        datatables which can be addressed by its index. Please note the
        the index of the datatables columns are increased by 1. So you
        will need to add 1 to the result of this method."""
        for num, col in enumerate(self.get_columns()):
            if col["name"] == name:
                return num
        return 0

    def get_default_sort_column(self):
        """Returns the name of the attribute of the clazz which is
        marked as field for default sorting in the *settings* section of
        the configuration. If no default sorting is configured then
        return the name of the attribute in the first column which is
        configured in the table"""
        settings = self.get_settings()
        if settings:
            def_sort = settings.get('default-sort-field')
            if def_sort:
                return def_sort
        return self.get_columns()[0].get('name')

    def get_default_sort_order(self):
        """Returns the ordering of the sort in the table """
        settings = self.get_settings()
        if settings:
            def_order = settings.get('default-sort-order')
            if def_order:
                return def_order
        return "asc"

    def get_default_search(self):
        """Returns the seaech filter of the items in the table """
        settings = self.get_settings()
        if settings:
            def_search = settings.get('default-search')
            if def_search:
                return def_search
        return []


def _load_overview_config(clazz):
    """Return a datastructure representing the overview
    configuration. The configuration is loaded from a JSON
    configuration file. The function will first try to load the
    application specific configuration. If this fails it will try to
    load it form the extension specific loaction or orign application
    and finally from ringo.  If no configuration can be found an
    exception is raised."""
    cfile = "%s.json" % clazz.__tablename__
    config = None
    name = clazz.__module__.split(".")[0]
    for appname in get_app_inheritance_path():
        try:
            # Always first try to load from the current application. No
            # matter what the current name is as name can be different from
            # the appname in case of loading forms for an extension. In this
            # case first try to load the form configuration from the
            # application to be able to overwrite the forms.
            config = open(get_path_to_overview_config(cfile, appname), "r")
            break
        except IOError:
	    # Silently ignore IOErrors here as is Ok when trying to load the
	    # configurations files while iterating over the possible config
	    # file locations. If the file can finally not be loaded an IOError
	    # is raised at the end.
            pass
    else:
        if name.startswith("ringo_"):
            config = open(get_path_to_overview_config(cfile,
                                                      name,
                                                      location="."), "r")
    # If we can't load the config file after searching in all locations, raise
    # an IOError. Hint: Maybe you missed to set the app.base config variable?
    if not config:
        raise IOError("Could not load table configuration for %s" % cfile)
    return json.load(config)


class Filter(object):
    """This class represents a custom filter used in Listings using the
    datatables JS extension. This class is used to give access to the
    relevant attribute of a filter. Some of the attributes are processed
    to be ready to be used directly in JS code."""

    def __init__(self, conf):
        self._conf = conf
        self.expr = self._conf.get("expr", "")
        self.field = self._conf.get("field", "")
        self.label = self._conf.get("label", "")
        self.type = self._conf.get("type", "checkbox")
        self.active = self._conf.get("active", True)

        # JS Options used in filter method
        if self._conf.get("regex", False):
            self.regex = "true"
        else:
            self.regex = "false"
        if self._conf.get("smart", True) and not self._conf.get("regex", False):
            self.smart = "true"
        else:
            self.smart = "false"
        if self._conf.get("caseinsensitive", True):
            self.caseinsensitive = "true"
        else:
            self.caseinsensitive = "false"
