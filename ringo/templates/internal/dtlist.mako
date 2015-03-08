<%
from ringo.lib.helpers import prettify
%>
<table class="table table-condensed table-striped table-bordered datatable-simple">
  <thead>
    <tr>
      % for field in tableconfig.get_columns():
      <th width="${field.get('width')}">${_(field.get('label'))}</th>
      % endfor
    </tr>
  </thead>
  <tbody>
    % for item in items:
      <%
      permission = None
      if s.has_permission("update", item, request):
        permission = "update"
      elif s.has_permission("read", item, request):
        permission = "read"
      %>
    <tr>
      % for field in tableconfig.get_columns():
      % if permission:
      <td onclick="openItem('${request.route_path(h.get_action_routename(clazz, permission), id=item.id)}')" class="link">
      % else:
      <td>
      % endif
          <%
            form_config = tableconfig.get_form_config()
            try:
              value = prettify(request, item.get_value(field.get('name'), expand=field.get('expand')))
            except AttributeError:
              value = "NaF"
          %>
          ## Escape value here
          % if isinstance(value, list):
            ${", ".join(_(v) for v in value) | h}
          % else:
            ${_(value)}
          % endif
      </td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
