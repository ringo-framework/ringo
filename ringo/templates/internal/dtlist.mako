<%
from ringo.lib.helpers import prettify
%>
%if tableconfig.is_paginated():
<div class="search-widget">
  <div class="row">
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
  </div>
</div>
% endif

<form id="data-table" name="data-table" role="form" action="${request.route_path(h.get_action_routename(clazz, 'bundle'))}" method="POST">
<table id="data" class="table table-condensed table-striped table-hover datatable-simple">
  <thead>
    <tr>
      % if bundled_actions:
      <th width="2em">
        <input type="checkbox" name="check_all" onclick="checkAll('id');">
      </th>
      % endif
      % for field in tableconfig.get_columns():
      <th width="${field.get('width')}">${_(field.get('label'))}</th>
      % endfor
    </tr>
  </thead>
  <tbody>
    % for item in items[listing.pagination_start:listing.pagination_end]:
      <%
      permission = None
      if s.has_permission("update", item, request):
        permission = "update"
      elif s.has_permission("read", item, request):
        permission = "read"
      %>
    <tr item-id="${item.id}">
      % if bundled_actions:
        <td>
          <input type="checkbox" name="id" value="${item.id}">
        </td>
      % endif
      % for field in tableconfig.get_columns():
        % if permission:
          <td onclick="openItem('${request.route_path(h.get_action_routename(clazz, permission), id=item.id)}')" class="link">
        % else:
          <td>
        % endif
          <%
            try:
              value = prettify(request, item.get_value(field.get('name'), expand=field.get('expand')))
            except AttributeError:
              value = "NaF"
          %>
          ## Escape value here
          % if isinstance(value, list):
            ${", ".join(_(v) for v in value)}
          % else:
            ${_(value)}
          % endif
        </td>
      % endfor 
    </tr>
    % endfor

    % if len(items) == 0:
    <tr>
      % if bundled_actions:
        <td colspan="${len(tableconfig.get_columns())+1}">
      % else:
        <td colspan="${len(tableconfig.get_columns())}">
      % endif
      ${_('No items found')}
      </td>
    </tr>
  % endif
  </tbody>
</table>
% if bundled_actions or tableconfig.is_paginated():
<div class="search-widget">
  <div class="row">
    <div class="col-xs-6">
      % if bundled_actions: 
      <input name="csrf_token" type="hidden" value="${request.session.get_csrf_token()}">
      <select class="form-control input-small" name="bundle_action" style="display:inline;width:auto;">
        % for action in bundled_actions:
          ##${action.bundle}
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
