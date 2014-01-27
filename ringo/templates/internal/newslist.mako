<%
import datetime
from ringo.lib.helpers import format_datetime
%>
<table class="table table-condensed table-striped table-bordered datatable-pageinated">
  <thead>
    <tr>
      % for field in tableconfig.get_columns():
      <th width="${field.get('width')}">${field.get('label')}</th>
      % endfor
      <th width="10"><span class="glyphicon glyphicon-check"></span></th>
    </tr>
  </thead>
  <tbody>
    % for item in items:
    % if s.has_permission("update", item, request):
      <tr onclick="openItem('${request.route_path(item.get_action_routename("update"), id=item.id)}')">
    % else:
      <tr onclick="openItem('${request.route_path(item.get_action_routename("read"), id=item.id)}')">
    % endif
      % for field in tableconfig.get_columns():
      <td>
          <%
            form_config = tableconfig.get_form_config()
            try:
              value = getattr(item, field.get('name'))
              if isinstance(value, datetime.datetime):
                value = format_datetime(value)
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
      <td><span class="glyphicon glyphicon-check"></span></td>
    </tr>
    % endfor
  </tbody>
</table>
