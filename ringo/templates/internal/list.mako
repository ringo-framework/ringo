<%
mapping = {'num_filters': len(listing.search_filter)}
def render_filter_link(request, field, value, clazz):
  out = []
  url = request.current_route_url()
  params = "form=search&search=%s&field=%s" % (value, field.get('name'))
  out.append('<a href="%s?%s"' % (url, params))
  out.append('class="filter"')
  out.append('title="Filter %s on %s in %s">' % (clazz.get_item_modul().get_label(plural=True), value, field.get('label')))
  out.append('%s</a>' % value)
  return " ".join(out)
%>
<div class="well well-small search-widget">
  <form name="search" class="form-inline" action="${request.current_route_url()}" method="POST">
    <input name="csrf_token" type="hidden" value="${request.session.get_csrf_token()}">
    <input name="form" type="hidden" value="search">
    <input name="search" type="text" class="input-large" value="${search}" placeholder="${_('Search for (Regexpr) in ...')}"/>
    <select name="field" class="input-small">
      <option value="">${_('All columns')}</option>
      % for field in tableconfig.get_columns():
        % if field.get('name') == search_field:
          <option value="${field.get('name')}" selected>${_(field.get('label'))}</option>
        % else:
          <option value="${field.get('name')}">${_(field.get('label'))}</option>
        % endif
      % endfor
    </select>
    <button class="btn">${_('Search')}</button>
    <div class="btn-group">
      <button class="btn dropdown-toggle" data-toggle="dropdown" tabindex="-1">${_('Options ')}<span class="caret"></span></button>
      <ul class="dropdown-menu">
          <li>
            <table class="table table-condensed">
              % for key, value in saved_searches.iteritems():
              <tr>
                <td>
                  <a tabindex="-1"
                  href="${request.current_route_url()}?form=search&saved=${key}">${_(value[2])}</a>
                </td>
                <td width="20">
                  <a class="pull-right" tabindex="-1" href="${request.current_route_url()}?form=search&delete=${key}"><i class="icon-remove"></i></a>
                </td>
              </tr>
              % endfor
            </table>
          </li>
        <li class="divider"></li>
        <li><a tabindex="-1" href="#" data-toggle="modal" data-target="#savequerydialog">${_('Save current search filter')}</a></li>
        <li><a tabindex="-1" href="${request.current_route_url()}?form=search&reset">${_('Reset current search filter')}</a></li>
      </ul>
    </div>
    % if len(listing.search_filter) > 0:
      <span class="muted"><small>(${_('${num_filter} filter applied', mapping=mapping )})</small></span>
    % endif
  </form>
</div>
<form id="data-table">
<table id="data" class="table table-striped table-hover table-condensed
table-bordered">
  <tr>
  % if enable_bundled_actions:
    <th width="2em">
      <input type="checkbox" name="check_all" onclick="checkAll('id');">
    </th>
  % endif
  % for field in tableconfig.get_columns():
    <th width="${field.get('width')}">
      % if request.session['%s.list.sort_order' % clazz.__tablename__] == "asc":
        <a
        href="${request.current_route_url()}?sort_field=${field.get('name')}&sort_order=desc">${_(field.get('label'))}</a>
      % else:
        <a
        href="${request.current_route_url()}?sort_field=${field.get('name')}&sort_order=asc">${_(field.get('label'))}</a>
      % endif
      % if request.session['%s.list.sort_field' % clazz.__tablename__] == field.get('name'):
        % if request.session['%s.list.sort_order' % clazz.__tablename__] == "asc":
          <i class="pull-right icon-arrow-up"></i>
        % else:
          <i class="pull-right icon-arrow-down"></i>
        % endif
      % endif
    </th>
  % endfor
  </tr>
  % for item in items:
  <tr onclick="openItem('${request.route_url(clazz.get_action_routename("read"), id=item.id)}')">
    % if enable_bundled_actions:
    <td>
      <input type="checkbox" name="id" value="${item.id}">
    </td>
    % endif
    % for field in tableconfig.get_columns():
    <td>
        <%
          form_config = tableconfig.get_form_config()
          try:
            value = getattr(item, field.get('name'))
          except AttributeError:
            value = "NaF"
        %>
        % if isinstance(value, list):
          ## TODO: Expandation needed here? As this are very likely
          ## linked items and the representation is determined by the
          ## items __unicode__ method (ti) <2013-10-05 12:31> -->
          <%
            links = []
            for v in value:
             links.append(render_filter_link(request, field, v, clazz))
          %>
          ${", ".join(links)}
        % else:
          ${render_filter_link(request, field, item.get_value(field.get('name')), clazz)}
        % endif
    </td>
    % endfor
  </tr>
  % endfor
  % if len(items) == 0:
  <tr>
    <td colspan="${len(tableconfig.get_columns())}">
    ${_('No items found')}
    </td>
  </tr>
  % endif
</table>
</form>

<div id="savequerydialog" class="modal hide fade">
  <form id="savequery" action="${request.current_route_url()}">
  <input name="csrf_token" type="hidden" value="${request.session.get_csrf_token()}">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>${_('Save current search filter')}</h3>
  </div>
  <div class="modal-body">
    <label for="save">${_('Queryname')}</label>
    <input type="textfield" id="save" name="save"/>
    <input type="hidden" name="form" value="search"/>
    <p><small>${_('Please insert a name for your query. It it will be selectable under this name in the options menu of the search after saving.')}</small></p>
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${_('Close')}</a>
    <input class="btn btn-primary" type="button" onclick="formSubmit()" value="${_('Save Query')}">
  </div>
  </form>
</div>

<script type="text/javascript">
function formSubmit() {
  document.getElementById("savequery").submit();
}
</script>
