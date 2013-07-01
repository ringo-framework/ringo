## Disable search for 0.2.2 release.
##<div class="well well-small search-widget">
##  <form name="search" class="form-inline" action="${request.current_route_url()}" method="POST">
##    <input name="form" type="hidden" value="search">
##    <input name="search" type="text" class="input-large" value="${search}" placeholder="Search for (Regexpr) in ..."/>
##    <select name="field" class="input-small">
##      <option value="">All fields</option>
##      % for field in headers:
##        % if field[0] == search_field:
##          <option value="${field[0]}" selected>${field[1]}</option>
##        % else:
##          <option value="${field[0]}">${field[1]}</option>
##        % endif
##      % endfor
##    </select>
##    <button type="submit" class="btn">Search</button>
##    % if len(listing.search_filter) > 0:
##      <span class="muted"><small>(${len(listing.search_filter)} filter applied)</small></span>
##    % endif
##  </form>
##</div>
<form id="data-table">
<table id="data" class="table table-striped table-hover table-condensed
table-bordered">
  <tr>
  % if enable_bundled_actions:
    <th width="2em">
      <input type="checkbox" name="check_all" onclick="checkAll('id');">
    </th>
  % endif
  % for field in headers:
    <th>
      % if request.session['%s.list.sort_order' % clazz.__tablename__] == "asc":
        <a href="${request.current_route_url()}?sort_field=${field[0]}&sort_order=desc">${field[1]}</a>
      % else:
        <a href="${request.current_route_url()}?sort_field=${field[0]}&sort_order=asc">${field[1]}</a>
      % endif
      % if request.session['%s.list.sort_field' % clazz.__tablename__] == field[0]:
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
    % for field in headers:
    <td>
        <% value = getattr(item, field[0]) %>
        ## Escape value here
        % if isinstance(value, list):
          ${", ".join(unicode(v) for v in value) | h}
        % else:
          ${value | h}
        % endif
    </td>
    % endfor
  </tr>
  % endfor
  % if len(items) == 0:
  <tr>
    <td colspan="${len(headers)}">
    No items found
    </td>
  </tr>
  % endif
</table>
</form>

<script type="text/javascript">
function openItem(url) {
  location.href = url;
};

function checkAll(checkId) {
  var inputs = document.getElementsByTagName("input");
  for (var i = 0; i < inputs.length; i++) {
      if (inputs[i].type == "checkbox" && inputs[i].name == checkId) {
          if(inputs[i].checked == true) {
              inputs[i].checked = false ;
          } else if (inputs[i].checked == false ) {
              inputs[i].checked = true ;
          }
      }
  }
}
</script>
