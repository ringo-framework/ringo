###############################################################################
##                           Table Header Helpers                            ##
###############################################################################

<%def name="render_table_header_checkbox(name, multiple=True)">
  <th width="20px" class="checkboxrow">
    % if multiple:
      <input type="checkbox" name="check_all" onclick="checkAll('${name}');">
    % endif
  </th>
</%def>

<%def name="render_table_header_cols(request, tableconfig)">
  % for num, col in enumerate(tableconfig.get_columns(request.user)):
    <th style="${'' if col.get('visible', True) else 'display: none;'}" 
        class="${num > 0 and 'hidden-xs'}"
        title="${col.get('title') or _(col.get('label'))}"
        width="${col.get('width')}">${_(col.get('label'))}
    </th>
  % endfor
</%def>

###############################################################################
##                            Table Body Helpers                             ##
###############################################################################


<%def name="render_table_body_cols(request, item, tableconfig, css_class='')">
  % for num, col in enumerate(tableconfig.get_columns(request.user)):
    <td class="${css_class}">
      ${render_value(request, item, col, tableconfig)}
    </td>
  % endfor
</%def>

<%def name="render_table_body_checkbox(name, value, selected, visible=True, checker='check')">
  <td>
    <span class="hidden">${"1" if selected else "0"}</span>
    <input type="checkbox" value="${value}" name="${name}" class="${'' if visible else 'hidden'}" ${'checked="checked"' if selected  else ''} onclick="${checker}('${name}', this);"/>
  </td>
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
