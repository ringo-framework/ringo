<table id="data" class="table table-striped table-hover table-condensed">
  <tr>
  % for field in headers:
    <th>
      ${field[1]}
    </th>
  % endfor
  </tr>
  % for item in items:
  <tr onclick="openItem('${request.route_url(clazz.get_action_routename("read"), id=item.id)}')">
    % for field in headers:
    <td>
        <% value = getattr(item, field[0]) %>
        ## Escape value here
        % if isinstance(value, list):
          ${", ".join(unicode(v) for v in value) | h}
        % else:
          ${value | h}
        % endif
    </td>
    % endfor
  </tr>
  % endfor
  % if len(items) == 0:
  <tr>
    <td colspan="${len(headers)}">
    No items found
    </td>
  </tr>
  % endif
</table>

<script language="JavaScript">
function openItem(url) {
  location.href = url;
}
</script>
