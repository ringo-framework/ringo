<table class="table table-condensed table-striped table-bordered datatable-simple">
  <thead>
    <tr>
      % for field in tableconfig.get_columns():
      <th width="${field.get('width')}">${field.get('label')}</th>
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
      <td onclick="openItem('${request.route_path(clazz.get_action_routename(permission), id=item.id)}')" class="link">
      % else:
      <td>
      % endif
          <%
            form_config = tableconfig.get_form_config()
            try:
              value = getattr(item, field.get('name'))
            except AttributeError:
              value = "NaF"
          %>
          ## Escape value here
          % if isinstance(value, list):
            ${", ".join(unicode(v) for v in value) | h}
          % else:
            ${value}
          % endif
      </td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
