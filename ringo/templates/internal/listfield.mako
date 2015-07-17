<%
from ringo.lib.helpers import prettify
import cgi
value = field.get_value() or []
if not isinstance(value, list):
  value = [value]
selected = [str(id) for id in value if id]
visible_items = []
hidden_items = []
for item in items:
  if item[2]:
    visible_items.append(item)
  else:
    hidden_items.append(item)

def render_item_link(request, clazz, permission, item, value, modal=False, backlink=True):
  out = []
  css_class = ["link"]
  # Only take the path of the url and ignore any previous search filters.
  url = request.route_path(h.get_action_routename(clazz, permission), id=item[0].id)
  if backlink:
    out.append('<a href="%s?backurl=%s" ' % (url, request.current_route_path()))
  else:
    out.append('<a href="%s" ' % (url))
  if modal:
    css_class.append("modalform")
  out.append('class="%s"' % " ".join(css_class))
  out.append('>')
  if hasattr(value, "render"):
    out.append(cgi.escape('%s' % value.render()))
  else:
    out.append(cgi.escape('%s' % value))
  out.append('</a>')
  return " ".join(out)
%>

% if field.renderer.showsearch == "true" and not field.is_readonly():
<table class="table table-condensed table-striped datatable-simple">
% else:
<table class="table table-condensed table-striped datatable-blank content-shorten">
% endif
  <thead>
    % if not field.is_readonly() and not field.renderer.hideadd == "true" and s.has_permission("create", clazz, request) and h.get_item_modul(request, clazz).has_action("create"):
    <tr class="table-toolbar">
      <th colspan="${len(tableconfig.get_columns())+1}">
        <a class="btn btn-primary btn-xs" href="#" title="${_('Add a new %s entry') % h.get_item_modul(request, clazz).get_label()}"
          onclick="addItem('${request.route_path(h.get_action_routename(clazz,
          "create"))}', '${field.name}', '${field.renderer.form}',
          '${field._form._item.id}', '${h.get_item_modul(request,
      pclazz).clazzpath}', '${field.renderer.backlink != 'false'}')"
      ><i class="glyphicon glyphicon-plus"></i> ${_('New')}</a>
      </th>
    </tr>
    % endif
    <tr>
    % if not field.is_readonly() and field.renderer.onlylinked != "true":
      <th width="20px">
        % if not field.renderer.multiple == "false":
          <input type="checkbox" name="check_all" onclick="checkAll('${field.name}');">
        % endif
      </th>
    % endif
      % for num, col in enumerate(tableconfig.get_columns()):
      <th class="${num > 0 and 'hidden-xs'}" width="${col.get('width')}">${_(col.get('label'))}</th>
      % endfor
    </tr>
  </thead>
  <tbody>
    % for item in visible_items:
      <%
      permission = None
      if s.has_permission("update", item[0], request):
        permission = "update"
      elif s.has_permission("read", item[0], request):
        permission = "read"
      elif not field.renderer.showall == "true":
        continue
      %>
      <tr>
      ## Readonly -> Do nothing
      % if not field.is_readonly():
        % if field.renderer.onlylinked != "true":
          <td>
            % if not field.renderer.multiple == "false":
              % if str(item[0].id) in selected:
                <input type="checkbox" value="${item[0].id}" name="${field.name}" checked="checked" onclick="check('${field.name}', this);"/>
              % else:
                <input type="checkbox" value="${item[0].id}" name="${field.name}" onclick="check('${field.name}', this);"/>
              % endif
            % else:
              % if str(item[0].id) in selected:
                <input type="checkbox" value="${item[0].id}" name="${field.name}" onclick="checkOne('${field.name}', this);" checked="checked"/>
              % else:
                <input type="checkbox" value="${item[0].id}" name="${field.name}" onclick="checkOne('${field.name}', this);"/>
              % endif
            % endif
          </td>
        % else:
          ## Hidden Checkbox for all linked items
          <input style="display:none" type="checkbox" value="${item[0].id}" name="${field.name}" checked="checked"/>
        % endif
      % endif
      % for num, col in enumerate(tableconfig.get_columns()):
        <%
          try:
            rvalue = prettify(request, item[0].get_value(col.get('name'), expand=col.get('expand')))
            if isinstance(rvalue, list):
              value = ", ".join(unicode(v) for v in rvalue)
            else:
              value = _(rvalue)
          except AttributeError:
            value = "NaF"
        %>
        <td class="${num > 0 and 'hidden-xs'}">
        % if permission and not field.renderer.nolinks == "true":
            ${h.literal(render_item_link(request, clazz, permission, item, value,
                              (field.renderer.openmodal == "true"),
                              (field.renderer.backlink != "false")))}
        % else:
          ${value}
        % endif
        </td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
% for item in hidden_items:
  % if str(item[0].id) in selected:
    <input style="display:none" type="checkbox" value="${item[0].id}" name="${field.name}" checked="checked"/>
  % endif
% endfor
