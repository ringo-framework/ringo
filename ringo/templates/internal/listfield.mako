% if field.renderer.showsearch == "true" and not field.readonly:
<table class="table table-condensed table-striped table-hover datatable-simple">
% else:
<table class="table table-condensed table-striped table-hover datatable-blank content-shorten">
% endif

<thead>
  % if not field.readonly and not field.renderer.hideadd == "true" and s.has_permission("create", clazz, request) and h.get_item_modul(request, clazz).has_action("create"):
    ${render_item_add_button(request, clazz, field)}
  % endif
  ${render_table_header(request, field, tableconfig)}
</thead>
<tbody>
  % for item in items:
    ## Only render linkable items or items which are already selected
    <%
      is_selected = item[0].id in selected_item_ids
    %>
    % if item[2] or is_selected:
      ${render_table_row(request, item, tableconfig, is_selected)}
    % endif
  % endfor
</tbody>
</table>

<%def name="render_value(request, item, col, tableconfig)">
  <%
  try:
    colrenderer = tableconfig.get_renderer(col)
    if colrenderer:
      value = colrenderer(request, item, col, tableconfig)
    else:
      rvalue = h.prettify(request, item[0].get_value(col.get('name'), expand=col.get('expand'), strict=col.get('strict', True)))
      if isinstance(rvalue, list):
        value = ", ".join(unicode(v) for v in rvalue)
      else:
        value = _(rvalue)
  except AttributeError:
    value = "NaF"
  %>
  ${value}
</%def>

<%def name="render_table_row(request, item, tableconfig, is_selected=False)">
  <%
    openmodal = field.renderer.openmodal == "true"
    backlink = field.renderer.backlink != "false"
    nolinks = field.renderer.nolinks == "true"
    permission = None
    url = None
    if not nolinks:
      if field.renderer.action:
        if s.has_permission(field.renderer.action, item[0], request):
          permission = field.renderer.action
      else:
        if s.has_permission("update", item[0], request):
          permission = "update"
        elif s.has_permission("read", item[0], request):
          permission = "read"
    if permission:
      url = request.route_path(h.get_action_routename(clazz, permission), id=item[0].id)
      if backlink:
        url += "?backurl=%s" % request.current_route_path()
  %>
  <tr item-id="${item[0].id}" ${'data-link={}'.format(url) if url else ''} ${'class="modalform"' if modalform else ''}>
    ## Render checkbox. A checkbox is rendered
    % if not field.readonly and field.renderer.onlylinked != "true":
      <td>
        <span class="hidden">${"1" if is_selected else "0"}</span>
        <input type="checkbox" 
               value="${item[0].id}" 
               name="${field.name}"
               class="${'' if item[2] else 'hidden'}"
               ${'checked="checked"' if is_selected  else ''}
               onclick="${'checkOne' if field.renderer.multiple == 'false' else 'check'}('${field.name}', this);"/>
      </td>
    % endif
    ## Render columns
    % for num, col in enumerate(tableconfig.get_columns(request.user)):
      <td class="${'link' if url else ''}">
        ${render_value(request, item, col, tableconfig)}
      </td>
    % endfor
  </tr>
</%def>

<%def name="render_table_header(request, field, tableconfig)">
  <tr>
  % if not field.readonly and field.renderer.onlylinked != "true":
    <th width="20px">
      % if not field.renderer.multiple == "false":
        <input type="checkbox" name="check_all" onclick="checkAll('${field.name}');">
      % endif
    </th>
  % endif
    % for num, col in enumerate(tableconfig.get_columns(request.user)):
    <th class="${num > 0 and 'hidden-xs'}" width="${col.get('width')}">${_(col.get('label'))}</th>
    % endfor
  </tr>
</%def>

<%def name="render_item_add_button(request, clazz, field)">
  <tr class="table-toolbar">
    <th colspan="${len(tableconfig.get_columns(request.user))+1}">
      <a class="btn btn-primary btn-xs hidden-print"
         title="${_('Add a new %s entry') % h.get_item_modul(request, clazz).get_label()}"
         href="${render_item_add_link(request,
                                      clazz,
                                      field.name,
                                      h.get_item_modul(request, pclazz).clazzpath,
                                      field._form._item.id,
                                      (field.renderer.backlink),
                                      field.renderer.form)}">
        <i class="glyphicon glyphicon-plus"></i> ${_('New')}</a>
    </th>
  </tr>
</%def>

<%def name="render_item_add_link(request, clazz, foreignkey, clazzpath, id, backlink, form)">
  <%
  query = {}
  query['addrelation'] = foreignkey+':'+clazzpath+':'+str(id)
  if backlink != 'false':
    query['backurl'] = request.current_route_path()
  if form:
    query['form'] = form
  %>
  ${request.route_path(h.get_action_routename(clazz, "create"), _query=query)}
</%def>
