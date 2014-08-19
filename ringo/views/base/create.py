import logging
from pyramid.httpexceptions import HTTPFound
from formbar.form import Form
from formbar.config import Config, parse
from ringo.lib.renderer import (
    add_renderers
)
from ringo.lib.helpers import import_model
from ringo.lib.security import has_permission
from ringo.lib.sql.cache import invalidate_cache
from ringo.model.mixins import Blobform
from ringo.model.form import Form as BlobformForm
from ringo.views.response import JSONResponse
from ringo.views.request import (
    handle_params,
    handle_history,
    handle_event,
    get_current_form_page
)

log = logging.getLogger(__name__)


def get_blobform_config(request, item, formname):
    """Helper function used in the create_ method to setup the create
    forms for blogform items. To create a new blogform item the
    creation is done in three steps:

    1. Stage 1: The user selects a form from a list
    2. Stage 2: The create dialog is rendered with the selected form
    3. Stage 3: The item is validated and saved.

    :request: current request
    :item: item to build the form
    :formname: name of the form in the formconfig
    :returns: formconfig, item used to build a form.

    """
    # First check if the fid parameter is provided
    fid = request.params.get('fid')
    blobform = request.params.get('blobforms')
    if fid:
        log.debug("Stage 3: User has submitted data to create a new item")
        setattr(item, 'fid', fid)
        formfactory = BlobformForm.get_item_factory()
        formconfig = Config(parse(formfactory.load(fid).definition))
        return item, formconfig.get_form(formname)
    elif blobform:
        log.debug("Stage 2: User has selected a blobform %s " % blobform)
        setattr(item, 'fid', blobform)
        formfactory = BlobformForm.get_item_factory()
        formconfig = Config(parse(formfactory.load(blobform).definition))
        return item, formconfig.get_form(formname)
    else:
        log.debug("Stage 1: User is selecting a blobform")
        modul = item.get_item_modul(request)
        formconfig = modul.get_form_config("blobform")
        return modul, formconfig


def create(request, callback=None, renderers={}):
    """Base view to create a new item of type clazz. This view will
    render a create form to create new items. It the user submits the
    data (POST) that the data will be validated and the new item will be
    saved to the database. Finally after saving on the POST-request the
    optional callback will be called.

    :request: The current request
    :callback: A callback function [function(request, item)] which
    returns the item again.
    :renderers: A optional dictionary of custom renderers which are
    provided to the form to render specific formelements.
    :returns: Dictionary with the following keys 'clazz', 'item', 'form'
    """
    clazz = request.context.__model__
    handle_history(request)
    params = handle_params(request)
    _ = request.translate
    rvalue = {}

    # Add ringo specific renderers
    renderers = add_renderers(renderers)

    # Create a new item
    factory = clazz.get_item_factory()
    item = factory.create(request.user)

    formname = request.session.get('%s.form' % clazz)
    if not formname:
        formname = 'create'

    # handle blobforms
    do_validate = True
    if isinstance(item, Blobform):
        item, formconfig = get_blobform_config(request, item, formname)
        do_validate = "blobforms" not in request.params
    else:
        formconfig = item.get_form_config(formname)

    form = Form(formconfig, item,
                request.db, translate=_,
                renderers=renderers,
                change_page_callback={'url': 'set_current_form_page',
                                      'item': clazz.__tablename__,
                                      'itemid': None},
                request=request,
                csrf_token=request.session.get_csrf_token(),
                eval_url='/rest/rule/evaluate')

    if request.POST and do_validate:
        item_label = clazz.get_item_modul(request).get_label()
        mapping = {'item_type': item_label}
        if form.validate(request.params):

            # Handle linking of the new item to antoher relation. The
            # relation was provided as GET parameter in the current
            # request and is now saved in the session.
            addrelation = request.session.get('%s.addrelation' % clazz)
            if addrelation:
                rrel, rclazz, rid = addrelation.split(':')
                parent = import_model(rclazz)
                pfactory = parent.get_item_factory()
                pitem = pfactory.load(rid)
                log.debug('Linking %s to %s in %s' % (item, pitem, rrel))
                tmpattr = getattr(pitem, rrel)
                tmpattr.append(item)

            # Save the item. Save validated values submitted from the
            # form into the new created item.
            sitem = item.save(form.data, request)
            msg = _('Created new ${item_type} successfull.',
                    mapping=mapping)
            log.info(msg)
            request.session.flash(msg, 'success')

            # handle create events
            handle_event(request, item, 'create')

            # Call callback. The callback is called as last action after
            # the rest of the saving has been done.
            if callback:
                sitem = callback(request, sitem)

            # Invalidate cache
            invalidate_cache()
            formname = request.session.get('%s.form' % clazz)
            if formname:
                del request.session['%s.form' % clazz]
                request.session.save()

            # Handle redirect after success.
            backurl = request.session.get('%s.backurl' % clazz)
            if backurl:
                # Redirect to the configured backurl.
                del request.session['%s.backurl' % clazz]
                request.session.save()
                return HTTPFound(location=backurl)
            else:
                # Set the URL the user will be redirected after the save
                # operation. URL depends on whether the user is allowed to
                # call the update page or not.
                if has_permission("update", item, request):
                    route_name = item.get_action_routename('update')
                    url = request.route_path(route_name, id=item.id)
                else:
                    route_name = item.get_action_routename('read')
                    url = request.route_path(route_name, id=item.id)
                return HTTPFound(location=url)
        else:
            msg = _('Error on validation the data'
                    ' for new ${item_type}', mapping=mapping)
            request.session.flash(msg, 'error')
    rvalue['clazz'] = clazz
    rvalue['item'] = item
    values = {'_roles': [str(r.name) for r in request.user.get_roles()]}
    values.update(params.get('values', {}))
    rvalue['form'] = form.render(values=values,
                                 page=get_current_form_page(clazz, request))
    return rvalue


def rest_create(request, callback=None):
    """Create a new item of type clazz. The item will be
    initialised with the data provided in the submitted POST request.
    The submitted data will be validated before the item is actually
    saved. If the submission fails the item is not saved in the
    database. In all cases the item is return as JSON object with the
    item and updated values back to the client. The JSON Response will
    include further details on the reason why the validation failed.

    :clazz: Class of item to create
    :request: Current request
    :returns: JSON object.

    """
    clazz = request.context.__model__
    # Create a new item.
    factory = clazz.get_item_factory()
    item = factory.create(request.user)
    # Initialise the create form for the item to be able to validate the
    # submitted data.
    form = Form(item.get_form_config('create'),
                item, request.db, translate=request.translate,
                csrf_token=request.session.get_csrf_token())
    if form.validate(request.params):
            sitem = form.save()
            return JSONResponse(True, sitem)
    else:
        # Validation fails! return item
        return JSONResponse(False, sitem)
