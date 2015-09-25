## TODO: Fix pagination in case that the simple overview is configured. In
## this case the pagination does not work correct and is disabled as
## workaround. (ti) <2015-09-25 09:07> 
% if bundled_actions or (tableconfig.is_paginated() and (tableconfig.is_advancedsearch(request.registry.settings.get("layout.advanced_overviews") == "true"))): 
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
    %if tableconfig.is_paginated() and (tableconfig.is_advancedsearch(request.registry.settings.get("layout.advanced_overviews") == "true")):
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
      <div id="pagination-size-selector" class="pull-right">
        ${_('Show')}
        <select class="form-control input-small" url="${request.current_route_path().split('?')[0]}">
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
% endif

