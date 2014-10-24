"""Functiont to work with forms."""
import os
from formbar.form import Form
from formbar.config import Config, load, parse
from formbar.helpers import get_css_files, get_js_files
from ringo.lib.cache import CACHE_FORM_CONFIG
from ringo.lib.helpers import get_path_to


def get_ownership_form(item, db, csrf_token, readonly=None):
    if readonly:
        config = _get_form_config('ringo', 'ownership.xml', 'ownership-form-read')
    else:
        config = _get_form_config('ringo', 'ownership.xml', 'ownership-form-update')
    return Form(config, item, db,
                csrf_token=csrf_token,
                eval_url='/rest/rule/evaluate')


def get_logbook_form(item, db, csrf_token, readonly=None):
    if readonly:
        config = _get_form_config('ringo', 'logbook.xml', 'logbook-form-read')
    else:
        config = _get_form_config('ringo', 'logbook.xml', 'logbook-form-update')
    return Form(config, item, db,
                csrf_token=csrf_token,
                eval_url='/rest/rule/evaluate')


def get_item_form(item, name, db, translate, renderers,
                  csrf_token, readonly=None):
    config = get_form_config(item, name)
    return Form(config, item, db,
                translate=translate,
                renderers=renderers,
                change_page_callback={'url': 'set_current_form_page',
                                      'item': item.__tablename__,
                                      'itemid': item.id},
                csrf_token=csrf_token,
                eval_url='/rest/rule/evaluate')


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
            config = _get_blobform_config(item.fid, formname)
        else:
            filename = "%s.xml" % item.__class__.__tablename__
            config = _get_form_config(name, filename, formname)
        CACHE_FORM_CONFIG.set(cachename, config)
    return CACHE_FORM_CONFIG.get(cachename)


def _get_form_config(name, filename, formname):
    """Return the file based configuration for a given form. The
    configuration tried to be loaded from the application first. If this
    fails it tries to load it from the extension and finally from the
    ringo application."""
    try:
        loaded_config = load(get_path_to_form_config(filename, name))
    except IOError:
        try:
            loaded_config = load(get_path_to_form_config(filename, name, location="."))
        except IOError:
            loaded_config = load(get_path_to_form_config(filename, "ringo"))
    return Config(loaded_config).get_form(formname)


def _get_blobform_config(fid, formname):
    """Return the blobform configuration for a given form."""
    from ringo.model.form import Form
    factory = Form.get_item_factory()
    form = factory.load(fid)
    return Config(parse(form.definition.encode('utf-8'))).get_form(formname)


formbar_css_filenames = []
def get_formbar_css():
    result = get_css_files()
    for filename, content in result:
        formbar_css_filenames.append(filename)
    return result


formbar_js_filenames = []
def get_formbar_js():
    result = get_js_files()
    for filename, content in result:
        formbar_js_filenames.append(filename)
    return result
