import logging
from pyramid.httpexceptions import HTTPFound
from formbar.form import Form
from ringo.model.mixins import Owned, Logged
from ringo.lib.security import has_permission
from ringo.lib.sql.cache import invalidate_cache
from ringo.lib.renderer import (
    add_renderers
)
from ringo.views.forms import (
    get_ownership_form,
    get_logbook_form
)
from ringo.views.request import (
    handle_params,
    handle_history,
    handle_event,
    get_item_from_request,
    get_current_form_page
)

log = logging.getLogger(__name__)


def update__(request):
    """Wrapper method to match default signature of a view method. Will
    add the missing clazz attribut and call the wrapped method with the
    correct parameters."""
    clazz = request.context.__model__
    return update_(clazz, request)


def update_(clazz, request, callback=None, renderers={}):
    item = get_item_from_request(request)
    handle_history(request)
    handle_params(clazz, request)
    _ = request.translate
    rvalue = {}

    # Add ringo specific renderers
    renderers = add_renderers(renderers)

    owner_form = get_ownership_form(item, request)
    logbook_form = get_logbook_form(item, request, readonly=True,
                                    renderers=renderers)
    item_form_name = request.session.get("%s.form" % clazz) or "update"
    item_form = Form(item.get_form_config(item_form_name),
                     item, request.db, translate=_,
                     renderers=renderers,
                     change_page_callback={'url': 'set_current_form_page',
                                           'item': clazz.__tablename__,
                                           'itemid': item.id},
                     request=request,
                     csrf_token=request.session.get_csrf_token(),
                     eval_url='/rest/rule/evaluate')

    if request.POST:
        # Check which form should handled. If the submitted data has the
        # key "owner" than handle the ownership form.
        if 'owner' in request.params:
            form = owner_form
        else:
            form = item_form

        item_label = clazz.get_item_modul(request).get_label()
        mapping = {'item_type': item_label, 'item': item}
        if form.validate(request.params):
            item.save(form.data, request)
            msg = _('Edited ${item_type} "${item}" successfull.',
                    mapping=mapping)
            log.info(msg)
            request.session.flash(msg, 'success')

            # handle update events
            handle_event(request, item, 'update')

            # Call callback. The callback is called as last action after
            # the rest of the saving has been done.
            if callback:
                item = callback(request, item)

            # Invalidate cache
            invalidate_cache()
            if request.session.get('%s.form' % clazz):
                del request.session['%s.form' % clazz]
                request.session.save()

            backurl = request.session.get('%s.backurl' % clazz)
            if backurl:
                # Redirect to the configured backurl.
                del request.session['%s.backurl' % clazz]
                request.session.save()
                return HTTPFound(location=backurl)
            else:
                # Handle redirect after success.
                # Check if the user is allowed to call the url after saving
                if has_permission("update", item, request):
                    route_name = item.get_action_routename('update')
                    url = request.route_path(route_name, id=item.id)
                else:
                    route_name = item.get_action_routename('read')
                    url = request.route_path(route_name, id=item.id)
                return HTTPFound(location=url)
        else:
            msg = _('Error on validation the data for '
                    '${item_type} "${item}".', mapping=mapping)
            log.info(msg)
            request.session.flash(msg, 'error')

    # Validate the form to generate the warnings if the form has not
    # been alreaded validated.
    if not item_form.validated:
        item_form.validate(None)

    rvalue['clazz'] = clazz
    rvalue['item'] = item
    if isinstance(item, Owned):
        rvalue['owner'] = owner_form.render()
    else:
        rvalue['owner'] = ""
    if isinstance(item, Logged):
        rvalue['logbook'] = logbook_form.render()
    else:
        rvalue['logbook'] = ""

    # Add ringo specific values into the renderered form
    values = {'_roles': [str(r.name) for r in request.user.get_roles()]}
    rvalue['form'] = item_form.render(values=values,
                                      page=get_current_form_page(clazz,
                                                                 request))
    return rvalue
