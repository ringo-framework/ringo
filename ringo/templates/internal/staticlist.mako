<%
from ringo.lib.helpers import prettify
from ringo.lib.renderer.lists import get_read_update_url
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
      data_link = get_read_update_url(request, item, clazz, listing.is_prefiltered_for_user())
      %>
      <tr item-id="${item.id}" data-link="${data_link}">
      % for field in tableconfig.get_columns(request.user):
        % if data_link:
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
