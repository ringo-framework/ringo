<%namespace file="/internal/selection.mako" name="selection_helpers"/>
% if field.renderer.showsearch == "true" and not field.readonly:
<table class="table table-condensed table-striped table-hover datatable-simple">
% else:
<table class="table table-condensed table-striped table-hover datatable-blank content-shorten">
% endif

<thead>
  % if not field.readonly and not field.renderer.hideadd == "true" and s.has_permission("create", clazz, request) and h.get_item_modul(request, clazz).has_action("create"):
    ${render_item_add_button(request, clazz, field)}
  % endif
  <tr>
  % if not field.readonly and field.renderer.onlylinked != "true":
    ${selection_helpers.render_table_header_checkbox(field.name, field.renderer.multiple != "false")}
  % endif
  ${selection_helpers.render_table_header_cols(request, tableconfig)}
  </tr>
</thead>

<tbody>
  % for item in items:
    ## Only render linkable items or items which are already selected
    <%
      is_selected = item[0].id in selected_item_ids
    %>
    % if item[2] or is_selected:
      <%
        if not field.renderer.nolinks == "true":
          url = url_getter(item[0], request, field.renderer.action, field.renderer.backlink != "false")
        else:
          url = None
      %>
      <tr item-id="${item[0].id}" ${'data-link={}'.format(url) if url else ''} ${'class="modalform"' if (field.renderer.openmodal == "true") else ''}>
      % if not field.readonly and field.renderer.onlylinked != "true":
        ${selection_helpers.render_table_body_checkbox(field.name, item[0].id, is_selected, item[2], ('checkOne' if field.renderer.multiple == 'false' else 'check'))}
      % endif
      ${selection_helpers.render_table_body_cols(request, item[0], tableconfig, 'link' if url else '')}
      </tr>
    % endif
  % endfor
</tbody>
</table>

<%def name="render_item_add_button(request, clazz, field)">
  <tr class="table-toolbar">
    <th colspan="${len(tableconfig.get_columns(request.user))+1}">
      <a class="btn btn-primary btn-xs hidden-print"
         data-original-title="${_('Add a new %s entry') % h.get_item_modul(request, clazz).get_label()}"
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
