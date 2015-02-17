"""Modul to with function to work with the table configuration"""
import logging
import os
import json
from ringo.lib.helpers import get_path_to, get_app_name
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
                        "filter": false
                    }
                ]
                "settings": {
                    "default-sort-field": "name"
                    "default-sort-order": "desc"
                    "auto-responsive": true
                }
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

    Further the table has some table wide configuration options:

    * *default-sort-field*: Name of the column which should be used as
      default sorting on the table. Defaults to the first column in the table.
    * *default-sort-order*: Sort order (desc, asc) Defaults to asc.
    * *auto-responsive*: If True than only the first column of a table
      will be displayed on small devices. Else you need to configure the
      "screen" attribute for the fields.
    * *pagination*: If True pagination of the results will be enabled.
      The table will have gui element to configure pagination of the
      table. Defaults to false.
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

    def is_autoresponsive(self):
        settings = self.get_settings()
        return settings.get("auto-responsive", True)

    def is_paginated(self):
        settings = self.get_settings()
        return settings.get("pagination", False)

    def get_columns(self):
        """Return a list of configured columns within the configuration.
        Each colum is a dictionary containing the one or more available
        conifguration attributes."""
        cols = []
        config = self.config.get(self.name)
        for col in config.get('columns'):
            cols.append(col)
        return cols

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
    # FIXME: Add support loading configurations in case of derived
    # models. In this case we should try to look for a
    # configuration in the application which inherits from a model.
    # If there is no configuration. Try to figure out from which
    # model it is derived and load the configuration of the base
    # class () <2015-02-17 15:57>
    try:
        # Always first try to load from the current application. No
        # matter what the current name is as name can be different from
        # the appname in case of loading forms for an extension. In this
        # case first try to load the form configuration from the
        # application to be able to overwrite the forms.
        config = open(get_path_to_overview_config(cfile, get_app_name()), "r")
    except IOError:
        try:
            # This path is working for extensions.
            if name.startswith("ringo_"):
                config = open(get_path_to_overview_config(cfile,
                                                          name,
                                                          location="."), "r")
            # This path is working for base config of the application.
            else:
                config = open(get_path_to_overview_config(cfile, name), "r")
        except IOError:
            # Final fallback try to load from ringo.
            config = open(get_path_to_overview_config(cfile, "ringo"), "r")
    return json.load(config)
