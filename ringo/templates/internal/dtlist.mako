<%
from ringo.lib.helpers import prettify
%>
<form id="data-table" name="data-table" role="form" action="${request.route_path(h.get_action_routename(clazz, 'bundle'))}" method="POST">
<table id="data" class="table table-condensed table-striped table-hover datatable-simple">
  <thead>
    <tr>
      % if bundled_actions and len(items) > 0:
      <th width="2em">
        <input type="checkbox" name="check_all" onclick="checkAll('id');">
      </th>
      % endif
      % for field in tableconfig.get_columns():
      <th width="${field.get('width')}">${_(field.get('label'))}</th>
      % endfor
    </tr>
  </thead>
  <tbody>
    % for item in items[listing.pagination_start:listing.pagination_end]:
      <%
      permission = None
      if s.has_permission("update", item, request):
        permission = "update"
      elif s.has_permission("read", item, request):
        permission = "read"
      %>
    <tr item-id="${item.id}" data-link="${request.route_path(h.get_action_routename(clazz, permission), id=item.id)}">
      % if bundled_actions:
        <td>
          <input type="checkbox" name="id" value="${item.id}">
        </td>
      % endif
      % for field in tableconfig.get_columns():
        % if permission:
          <td class="link">
        % else:
          <td>
        % endif
          <%
            try:
              value = prettify(request, item.get_value(field.get('name'), expand=field.get('expand')))
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

<%include file="list_footer.mako"/>
