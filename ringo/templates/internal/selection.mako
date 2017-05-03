###############################################################################
##                           Table Header Helpers                            ##
###############################################################################

<%def name="render_table_header_checkbox(name, multiple=True)">
  <th width="20px">
    % if multiple:
      <input type="checkbox" name="check_all" onclick="checkAll('${name}');">
    % endif
  </th>
</%def>

<%def name="render_table_header_cols(request, tableconfig)">
  % for num, col in enumerate(tableconfig.get_columns(request.user)):
    <th class="${num > 0 and 'hidden-xs'}" width="${col.get('width')}">${_(col.get('label'))}</th>
  % endfor
</%def>

###############################################################################
##                               Value Helpers                               ##
###############################################################################

<%def name="render_value(request, item, col, tableconfig)">
  <%
  try:
    colrenderer = tableconfig.get_renderer(col)
    if colrenderer:
      value = colrenderer(request, item, col, tableconfig)
    else:
      rvalue = h.prettify(request, item.get_value(col.get('name'), expand=col.get('expand'), strict=col.get('strict', True)))
      if isinstance(rvalue, list):
        value = ", ".join(unicode(v) for v in rvalue)
      else:
        value = _(rvalue)
  except AttributeError:
    value = "NaF"
  %>
  ${value}
</%def>
