<%
from ringo.lib.helpers import prettify
%>
<table id="${tableid}" class="table table-condensed table-striped table-hover">
  <thead>
    <tr>
      % for field in tableconfig.get_columns(request.user):
        <th width="${field.get('width')}" title="${field.get('title') or _(field.get('label'))}">${_(field.get('label'))}</th>
      % endfor
    </tr>
  </thead>
  <tbody>
    % for item in items[listing.pagination_start:listing.pagination_end]:
      <%
      permission = None
      data_link = "#"
      if s.has_permission("update", item, request):
        permission = "update"
        data_link = request.route_path(h.get_action_routename(clazz, permission), id=item.id)
      elif s.has_permission("read", item, request):
        permission = "read"
        data_link = request.route_path(h.get_action_routename(clazz, permission), id=item.id)
      %>
      <tr item-id="${item.id}" data-link="${data_link}">
      % for field in tableconfig.get_columns(request.user):
        % if permission:
          <td class="link">
        % else:
          <td>
        % endif
          <%
            try:
              value = _(prettify(request, item.get_value(field.get('name'), expand=field.get('expand'))))
            except AttributeError:
              value = "NaF"
          %>
          ${value}
        </td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
