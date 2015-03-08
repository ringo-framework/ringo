<%
url = request.current_route_path().split("?")[0]
mapping = {'num_filters': len(listing.search_filter)}
def render_filter_link(request, field, value, clazz):
  out = []
  # Only take the path of the url and ignore any previous search filters.
  url = request.current_route_path().split("?")[0]
  params = "form=search&search=%s&field=%s" % (value, field.get('name'))
  out.append('<a href="%s?%s" data-toggle="tooltip"' % (url, params))
  out.append('class="link filter"')
  out.append('title="Filter %s on %s in %s">' % (h.get_item_modul(request, clazz).get_label(plural=True), value, field.get('label')))
  if hasattr(value, "render"):
    out.append('%s</a>' % _(value.render()))
  else:
    out.append('%s</a>' % _(value))
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
<div class="search-widget">
  <div class="row">
    <div class="col-xs-9">
      <form name="search" class="form-inline" role="form" action="${url}" method="POST">
        <input name="csrf_token" type="hidden" value="${request.session.get_csrf_token()}">
        <input name="form" type="hidden" value="search">
        <div class="form-group">
          <label class="sr-only" for="search">${_('Search')}</label>
          <input name="search" class="form-control input-large" type="text" value="${search}" placeholder="${_('Search for in ...')}"/>
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
        <button class="btn btn-default">
        % if regexpr or request.session.get('%s.list.search.regexpr' % clazz.__tablename__, False):
            ${_('Search+')}
        % else:
            ${_('Search')}
        % endif
        </button>
        <div class="btn-group">
          <button class="btn btn-default dropdown-toggle" data-toggle="dropdown" tabindex="-1">${_('Options ')}<span class="caret"></span></button>
          <ul class="dropdown-menu">
              <li>
                <table class="table table-condensed">
                  % for key, value in saved_searches.iteritems():
                  <tr>
                    <td>
                      <a tabindex="-1"
                      href="${url}?form=search&saved=${key}">${_(value[2])}</a>
                    </td>
                    <td width="20">
                      <a class="pull-right" tabindex="-1" href="${url}?form=search&delete=${key}"><i class="glyphicon glyphicon-remove"></i></a>
                    </td>
                  </tr>
                  % endfor
                </table>
              </li>
            <li class="divider"></li>
            <li><a tabindex="-1" href="#" data-toggle="modal" data-target="#savequerydialog">${_('Save current search filter')}</a></li>
            <li><a tabindex="-1" href="${url}?form=search&reset">${_('Reset current search filter')}</a></li>
            % if request.session.get('%s.list.search.regexpr' % clazz.__tablename__, False):
              <li><a tabindex="-1" href="${url}?form=search&disableregexpr">${_('Disable regexpr in search')}</a></li>
            % else:
              <li><a tabindex="-1" href="${url}?form=search&enableregexpr">${_('Enable regexpr in search')}</a></li>
            % endif
          </ul>
        </div>
        % if len(listing.search_filter) > 0:
          <span class="muted"><small>(${_('${num_filter} filter applied', mapping=mapping )})</small></span>
        % endif
      </form>
    </div>
    %if tableconfig.is_paginated(): 
    <div class="col-xs-3">
      <div class="pull-right">
        ${_('Show')}
        <select id="pagination-size-selector" class="form-control input-small" url="${request.current_route_path().split('?')[0]}">
          <option value="25" ${listing.pagination_size == 25 and 'selected'}>25</option>
          <option value="50" ${listing.pagination_size == 50 and 'selected'}>50</option>
          <option value="100" ${listing.pagination_size == 100 and 'selected'}>100</option>
          <option value="250" ${listing.pagination_size == 250 and 'selected'}>250</option>
          <option value="500" ${listing.pagination_size == 500 and 'selected'}>500</option>
          <option value="" ${listing.pagination_size == None and 'selected'}>All</option>
        </select>
        ${_('items')}
      </div>
    </div>
    % endif
  </div>
</div>
<form id="data-table" name="data-table" role="form" action="${request.route_path(h.get_action_routename(clazz, 'bundle'))}" method="POST">
<table id="data" class="table table-striped table-hover table-condensed">
  <tr>
  % if enable_bundled_actions:
    <th width="2em">
      <input type="checkbox" name="check_all" onclick="checkAll('id');">
    </th>
  % endif
  % for num, field in enumerate(tableconfig.get_columns()):
    % if autoresponsive:
      <th width="${field.get('width')}" class="${num > 0 and 'hidden-xs'}">
    % else:
      <th width="${field.get('width')}" class="${render_responsive_class(field.get('screen'))}">
    % endif
      % if request.session['%s.list.sort_order' % clazz.__tablename__] == "asc":
        <a
        href="${request.current_route_path().split('?')[0]}?sort_field=${field.get('name')}&sort_order=desc">${_(field.get('label'))}</a>
      % else:
        <a
        href="${request.current_route_path().split('?')[0]}?sort_field=${field.get('name')}&sort_order=asc">${_(field.get('label'))}</a>
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
  % for item in items[listing.pagination_start:listing.pagination_end]:
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
        <td class="${num > 0 and 'hidden-xs'}">
      % else:
        <td class="${render_responsive_class(field.get('screen'))}">
      % endif
        <%
            try:
              value = h.prettify(request, item.get_value(field.get('name'), expand=field.get('expand')))
            except:
              value = "NaF"
        %>
        % if field.get('filter'):
          ## Render a filter link. A filter link will a shortcut to tritter a
          ## a new search based on the clicked value.
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
            ${render_filter_link(request, field, value, clazz)}
          % endif
        % else:
          % if isinstance(value, list):
            <%
              x = []
              for v in value:
                if hasattr(v, "render"):
                  x.append(v.render())
                else:
                  x.append(_(v))
                endif
              endfor
              value = ", ".join(x)
             %>
        % endif
        ## Render a usual Link which will open the item.
        <a class="link" title="${_('Open item in %s mode') % _(permission.capitalize())}" href="${request.route_path(h.get_action_routename(clazz, permission), id=item.id)}">${_(value)}</a>
        % endif
    </td>
    % endfor
  </tr>
  % endfor
  % if len(items) == 0:
  <tr>
    % if enable_bundled_actions:
      <td colspan="${len(tableconfig.get_columns())+1}">
    % else:
      <td colspan="${len(tableconfig.get_columns())}">
    % endif
    ${_('No items found')}
    </td>
  </tr>
  % endif
</table>
% if enable_bundled_actions or tableconfig.is_paginated():
<div class="search-widget">
  <div class="row">
    <div class="col-xs-6">
      % if enable_bundled_actions: 
      <input name="csrf_token" type="hidden" value="${request.session.get_csrf_token()}">
      <select class="form-control input-small" name="bundle_action" style="display:inline;width:auto;">
        % for action in h.get_item_actions(request, clazz):
          ${action.bundle}
          % if action.bundle:
            <option value="${action.name}">${_(action.name)}</option>
          % endif
        % endfor
      </select>
      <input class="btn btn-default input-small" type="submit" value="${_('Perform')}"/>
      % endif
    </div>
    %if tableconfig.is_paginated(): 
    <div class="col-xs-6">
      <div class="pull-right text-right">
        <div>
          <nav>
            <ul class="pagination">
              % if listing.pagination_current == 0:
                <li class="disabled"><a href="#">&laquo;</a></li>
              % else:
                <li><a href="${request.current_route_path().split('?')[0]}?pagination_page=${listing.pagination_current-1}">&laquo;</a></li>
              % endif
              % if listing.pagination_pages > 9:
                % for page in range(listing.pagination_first, listing.pagination_last):
                  <li class="${(page == listing.pagination_current) and 'active'}"><a href="${request.current_route_path().split('?')[0]}?pagination_page=${page}">${page+1}<span class="sr-only">(current)</span></a></li>
                % endfor
              % else:
                % for page in range(listing.pagination_pages):
                  <li class="${(page == listing.pagination_current) and 'active'}"><a href="${request.current_route_path().split('?')[0]}?pagination_page=${page}">${page+1}<span class="sr-only">(current)</span></a></li>
                % endfor
              % endif
              % if listing.pagination_pages == listing.pagination_current+1:
                <li class="disabled"><a href="#">&raquo;</a></li>
              % else:
                <li><a href="${request.current_route_path().split('?')[0]}?pagination_page=${listing.pagination_current+1}">&raquo;</a></li>
              % endif
            </ul>
          </nav>
        </div>
      </div>
    </div>
    % endif
  </div>
</div>
% endif
</form>

<div class="modal fade" id="savequerydialog">
  <form id="savequery" action="${url}">
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
  </form>
</div>

<script type="text/javascript">
function formSubmit() {
  document.getElementById("savequery").submit();
}
</script>
