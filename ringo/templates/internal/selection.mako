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
