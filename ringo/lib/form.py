"""Functiont to work with forms."""
import os
import inspect
from threading import Lock
from formbar.form import Form
from formbar.config import Config, load, parse
from formbar.helpers import get_css_files, get_js_files
from ringo.lib.cache import CACHE_FORM_CONFIG
from ringo.lib.helpers import (
    get_path_to,
    get_app_inheritance_path
)

formbar_css_filenames = []
formbar_js_filenames = []
form_lock = Lock()


def get_eval_url():
    """Returns the REST API endpoint for form evaluation"""
    return '/rest/rule/evaluate'


def get_ownership_form(item, db, csrf_token, eval_url,
                       readonly=None, url_prefix=None, locale=None,
                       translate=None):
    if readonly:
        config = get_form_config_from_file('ringo', 'ownership.xml',
                                           'ownership-form-read')
    else:
        config = get_form_config_from_file('ringo', 'ownership.xml',
                                           'ownership-form-update')
    return Form(config, item, db,
                csrf_token=csrf_token,
                eval_url=eval_url,
                url_prefix=url_prefix,
                locale=locale,
                translate=translate)


def get_path_to_form_config(filename, app=None, location=None):
    """Returns the path to the given form configuration. The filename
    should be realtive to the default `location` for the configurations
    in the given `app`.

    :file: Name of the form condifguration.
    :app: You can define the name of the application from where the form
    should be loaded. If no name is provied the code will search along
    the inheritance path of the current application and return the first
    form configuration it can find. Returns None if no configuration can
    be found.
    :location: Default is 'views/forms' you can define an alternative location.
    :returns: Absolute path to the configuration file

    """
    if location is None:
        location = "views/forms"
    if app is None:
        for app in get_app_inheritance_path():
            path = get_path_to(os.path.join(location, filename), app)
            if os.path.exists(path):
                return path
        return path
    else:
        return get_path_to(os.path.join(location, filename), app)


def get_form_config(item, formname):
    """Return the configuration for a given form. The function can
    handle usuall filebased form configurations and blobforms. The
    decision if the item is an instance of the a Blobform is done by
    checking the "fid" foreign key to a form definiton. If present we
    assume that the item is a blobform item.

    :item: Item or class for which the want to get the form
    :formname: name of the form which should be returned
    :returns: Formconfig
    """
    if inspect.isclass(item):
        cachename = "%s.%s" % (item.__name__, formname)
        filename = "%s.xml" % item.__tablename__
    else:
        cachename = "%s.%s" % (item.__class__.__name__, formname)
        filename = "%s.xml" % item.__class__.__tablename__
    name = item.__module__.split(".")[0]

    with form_lock:
        if not CACHE_FORM_CONFIG.get(cachename):
            if hasattr(item, 'fid'):
                config = get_form_config_from_db(item.fid, formname)
            else:
                config = get_form_config_from_file(name, filename, formname)
            CACHE_FORM_CONFIG.set(cachename, config)
    return CACHE_FORM_CONFIG.get(cachename)


def get_form_config_from_file(name, filename, formname):
    """Return the file based configuration for a given form. The
    configuration tried to be loaded from the current application (and
    its origins) first.  If this fails it tries to load it from the
    extension."""
    loaded_config = None
    try:
        path = get_path_to_form_config(filename)
        if os.path.exists(path):
            loaded_config = load(path)
        elif name.startswith("ringo_"):
            loaded_config = load(get_path_to_form_config(filename,
                                                         name, location="."))
    except:
        pass
    # If we can't load the config file, raise an IOError. Hint: Maybe
    # you missed to set the app.base config variable?
    if loaded_config is None:
        raise IOError("Could not load form configuration for %s" % filename)
    return Config(loaded_config).get_form(formname)


def get_form_config_from_db(fid, formname):
    """Return the blobform configuration for a given form."""
    from ringo.model.form import Form
    factory = Form.get_item_factory()
    form = factory.load(fid)
    return Config(parse(form.definition.encode('utf-8'))).get_form(formname)


def get_formbar_css():
    result = get_css_files()
    for filename, content in result:
        formbar_css_filenames.append(filename)
    return result


def get_formbar_js():
    result = get_js_files()
    for filename, content in result:
        formbar_js_filenames.append(filename)
    return result
