import logging
from pyramid.view import view_config

from formbar.renderer import FieldRenderer
from ringo.views.base import list_, create_, update_, read_, delete_
from ringo.views.json import (
    list_ as json_list,
    create_ as json_create,
    update_ as json_update,
    read_ as json_read,
    delete_ as json_delete
)
from ringo.model.comment import Comment

log = logging.getLogger(__name__)


class CommentRenderer(FieldRenderer):
    """Custom Renderer for the comment listing"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)

    def _render_info(self, comment):
        html = []
        html.append("<small>")
        html.append('<a href="/comments/read/%s">#%s</a>'
                    % (comment.id, comment.id))
        html.append(" | ")
        html.append("<bold>" + unicode(comment.owner.profile[0]) + "</bold>")
        html.append(" | ")
        str_updated = comment.updated.strftime("%y.%m.%d %H:%M")
        str_created = comment.created.strftime("%y.%m.%d %H:%M")
        html.append(str_created)
        if str_updated != str_created:
            html.append(" | (")
            html.append(str_updated)
            html.append(")</small>")
        return html

    def _render_body(self, comment):
        html = []
        html.append(comment.text.replace('\n', '<br>') or "")
        return html

    def render(self):
        html = []
        comments = self._field._form._item.comments
        html.append('<label for="">%s (%s)</lable>'
                    % (self._field.label, len(comments)))
        for comment in comments[::-1]:
            html.append('<input type="checkbox" name="%s" value="%s"'
                        ' style="display:none"/>'
                        % (self._field.name, comment.id))
            html.append('<div class="readonlyfield">')
            html.append("<table>")
            html.append("<tr >")
            html.append("<td>")
            html.extend(self._render_body(comment))
            html.append("</td>")
            html.append("<tr>")
            html.append('<td>')
            html.extend(self._render_info(comment))
            html.append("</td>")
            html.append("</tr>")
            html.append("</table>")
            html.append("</div>")
        return "".join(html)

###########################################################################
#                                HTML VIEW                                #
###########################################################################


#@view_config(route_name=Comment.get_action_routename('list'),
#             renderer='/default/list.mako',
#             permission='list')
#def list(request):
#    return list_(Comment, request)


#@view_config(route_name=Comment.get_action_routename('create'),
#             renderer='/default/create.mako',
#             permission='create')
#def create(request):
#    return create_(Comment, request)


@view_config(route_name=Comment.get_action_routename('update'),
             renderer='/default/update.mako',
             permission='update')
def update(request):
    return update_(Comment, request)


@view_config(route_name=Comment.get_action_routename('read'),
             renderer='/default/read.mako',
             permission='read')
def read(request):
    return read_(Comment, request)


@view_config(route_name=Comment.get_action_routename('delete'),
             renderer='/default/confirm.mako',
             permission='delete')
def delete(request):
    return delete_(Comment, request)

###########################################################################
#                              REST SERVIVE                               #
###########################################################################


#@view_config(route_name=Comment.get_action_routename('list', prefix="rest"),
#             renderer='json',
#             request_method="GET",
#             permission='list'
#             )
#def rest_list(request):
#    return json_list(Comment, request)


#@view_config(route_name=Comment.get_action_routename('create', prefix="rest"),
#             renderer='json',
#             request_method="POST",
#             permission='create')
#def rest_create(request):
#    return json_create(Comment, request)


@view_config(route_name=Comment.get_action_routename('read', prefix="rest"),
             renderer='json',
             request_method="GET",
             permission='read')
def rest_read(request):
    return json_read(Comment, request)


@view_config(route_name=Comment.get_action_routename('update', prefix="rest"),
             renderer='json',
             request_method="PUT",
             permission='update')
def rest_update(request):
    return json_update(Comment, request)


@view_config(route_name=Comment.get_action_routename('delete', prefix="rest"),
             renderer='json',
             request_method="DELETE",
             permission='delete')
def rest_delete(request):
    return json_delete(Comment, request)
