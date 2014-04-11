<%
mapping = {'num_filters': len(listing.search_filter)}
def render_filter_link(request, field, value, clazz):
  out = []
  url = request.current_route_url()
  params = "form=search&search=%s&field=%s" % (value, field.get('name'))
  out.append('<a href="%s?%s" data-toggle="tooltip"' % (url, params))
  out.append('class="filter"')
  out.append('title="Filter %s on %s in %s">' % (clazz.get_item_modul().get_label(plural=True), value, field.get('label')))
  if hasattr(value, "render"):
    out.append('%s</a>' % value.render())
  else:
    out.append('%s</a>' % value)
  return " ".join(out)

def render_responsive_class(visibleonsize):
  """Will return a string containing BS3 responsve classes to hide
  elements on different screen sizes."""
  if not visibleonsize:
    return ""
  elif visibleonsize == "small":
    return ""
  elif visibleonsize == "medium":
    return "hidden-xs"
  elif visibleonsize == "large":
    return "hidden-sm hidden-xs"
  elif visibleonsize == "xlarge":
    return "hidden-md hidden-sm hidden-xs"
  else:
    return ""

autoresponsive = tableconfig.is_autoresponsive()
%>
<div class="well well-small search-widget">
  <form name="search" class="form-inline" role="form" action="${request.current_route_url()}" method="POST">
    <input name="csrf_token" type="hidden" value="${request.session.get_csrf_token()}">
    <input name="form" type="hidden" value="search">
    <div class="form-group">
      <label class="sr-only" for="search">${_('Search')}</label>
      <input name="search" class="form-control input-large" type="text" value="${search}" placeholder="${_('Search for (Regexpr) in ...')}"/>
    </div>
    <div class="form-group">
      <label class="sr-only" for="field">${_('Fields')}</label>
      <select name="field"  class="form-control input-small">
        <option value="">${_('All columns')}</option>
        % for field in tableconfig.get_columns():
          % if field.get('name') == search_field:
            <option value="${field.get('name')}" selected>${_(field.get('label'))}</option>
          % else:
            <option value="${field.get('name')}">${_(field.get('label'))}</option>
          % endif
        % endfor
      </select>
    </div>
    <button class="btn btn-default">${_('Search')}</button>
    <div class="btn-group">
      <button class="btn btn-default dropdown-toggle" data-toggle="dropdown" tabindex="-1">${_('Options ')}<span class="caret"></span></button>
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
<form id="data-table" name="data-table" role="form" action="${request.route_path(clazz.get_action_routename('bundle'))}" method="POST">
<table id="data" class="table table-striped table-hover table-condensed
table-bordered">
  <tr>
  % if enable_bundled_actions:
    <th width="2em">
      <input type="checkbox" name="check_all" onclick="checkAll('id');">
    </th>
  % endif
  % for num, field in enumerate(tableconfig.get_columns()):
    % if autoresponsive:
      <th width="${field.get('width')}" class="${num > 0 and 'hidden-xs'}"</th>
    % else:
      <th width="${field.get('width')}" class="${render_responsive_class(field.get('screen'))}"</th>
    % endif
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
    <%
    permission = None
    if s.has_permission("update", item, request):
      permission = "update"
    elif s.has_permission("read", item, request):
      permission = "read"
    %>
    <tr>
    % if enable_bundled_actions:
    <td>
      <input type="checkbox" name="id" value="${item.id}">
    </td>
    % endif
    % for num, field in enumerate(tableconfig.get_columns()):
      % if autoresponsive:
        <td onclick="openItem('${request.route_path(clazz.get_action_routename(permission), id=item.id)}')" class="${num > 0 and 'hidden-xs'} link">
      % else:
        <td onclick="openItem('${request.route_path(clazz.get_action_routename(permission), id=item.id)}')" class="${render_responsive_class(field.get('screen'))} link">
      % endif
        <%
            try:
              value = h.prettify(request, getattr(item, field.get('name')))
            except:
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
          % if field.get('expand'):
            ${render_filter_link(request, field, item.get_value(field.get('name')), clazz)}
          % else:
            ${render_filter_link(request, field, value, clazz)}
          % endif
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
% if enable_bundled_actions:
  <div class="well well-small">
    <input name="csrf_token" type="hidden" value="${request.session.get_csrf_token()}">
    <select class="form-control input-small" name="bundle_action" style="display:inline;width:auto;">
      % for action in clazz.get_item_actions():
        ${action.bundle}
        % if action.bundle:
          <option value="${action.name}">${action.name}</option>
        % endif
      % endfor
    </select>
    <input class="btn btn-default input-small" type="submit" value="${_('Perform')}"/>
  </div>
% endif
</form>

<div class="modal fade" id="savequerydialog">
  <form id="savequery" action="${request.current_route_url()}">
  <input name="csrf_token" type="hidden" value="${request.session.get_csrf_token()}">
  <div class="modal-dialog">
    <div class="panel panel-default">
      <div class="panel-heading"><strong>${_('Save current search filter')}</strong></div>
        <div class="panel-body">
          <label for="save">${_('Queryname')}</label>
          <input type="textfield" id="save" name="save"/>
          <input type="hidden" name="form" value="search"/>
          <p><small>${_('Please insert a name for your query. It it will be selectable under this name in the options menu of the search after saving.')}</small></p>
        </div>
        <div class="panel-footer">
          <input class="btn btn-primary" type="button" onclick="formSubmit()" value="${_('Save Query')}">
          <a href="#" class="btn btn-default" data-dismiss="modal">${_('Close')}</a>
        </div>
      </div>
    </div>
  </div>
</div>

<script type="text/javascript">
function formSubmit() {
  document.getElementById("savequery").submit();
}
</script>
