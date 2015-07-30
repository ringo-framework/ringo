"""Functiont to work with forms."""
import os
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


def get_item_form(item, name, db, translate, renderers,
                  csrf_token, readonly=None):
    # TODO: Check if this method is ever called. I think the
    # get_item_form in view/helpers is the only called method. (torsten)
    # <2015-01-12 21:32>
    config = get_form_config(item, name)
    return Form(config, item, db,
                translate=translate,
                renderers=renderers,
                change_page_callback={'url': 'set_current_form_page',
                                      'item': item.__tablename__,
                                      'itemid': item.id},
                csrf_token=csrf_token,
                eval_url=eval_url)


def get_path_to_form_config(filename, app=None, location=None):
    """Returns the path the the given form configuration. The file name
    should be realtive to the default location for the configurations.

    :file: filename
    :returns: Absolute path to the configuration file

    """
    if location is None:
        location = "views/forms"
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
    cachename = "%s.%s" % (item.__class__.__name__, formname)
    name = item.__module__.split(".")[0]
    if not CACHE_FORM_CONFIG.get(cachename):
        if hasattr(item, 'fid'):
            config = get_form_config_from_db(item.fid, formname)
        else:
            filename = "%s.xml" % item.__class__.__tablename__
            config = get_form_config_from_file(name, filename, formname)
        CACHE_FORM_CONFIG.set(cachename, config)
    return CACHE_FORM_CONFIG.get(cachename)


def get_form_config_from_file(name, filename, formname):
    """Return the file based configuration for a given form. The
    configuration tried to be loaded from the current application first.
    If this fails it tries to load it from the extension or orign
    application and finally from the ringo application."""
    loaded_config = None
    for appname in get_app_inheritance_path():
        try:
            # Always first try to load from the current application. No
            # matter what the current name is as name can be different from
            # the appname in case of loading forms for an extension. In this
            # case first try to load the form configuration from the
            # application to be able to overwrite the forms.
            loaded_config = load(get_path_to_form_config(filename,
                                                         appname))
            break
        except IOError:
        # Silently ignore IOErrors here as is Ok when trying to load the
        # configurations files while iterating over the possible config
        # file locations. If the file can finally not be loaded an IOError
        # is raised at the end.
            pass
    else:
        if name.startswith("ringo_"):
            loaded_config = load(get_path_to_form_config(filename, name,
                                                         location="."))
    # If we can't load the config file after searching in all locations, raise
    # an IOError. Hint: Maybe you missed to set the app.base config variable?
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
