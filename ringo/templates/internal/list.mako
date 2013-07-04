<div class="well well-small search-widget">
  <form name="search" class="form-inline" action="${request.current_route_url()}" method="POST">
    <input name="form" type="hidden" value="search">
    <input name="search" type="text" class="input-large" value="${search}" placeholder="Search for (Regexpr) in ..."/>
    <select name="field" class="input-small">
      <option value="">All fields</option>
      % for field in headers:
        % if field[0] == search_field:
          <option value="${field[0]}" selected>${field[1]}</option>
        % else:
          <option value="${field[0]}">${field[1]}</option>
        % endif
      % endfor
    </select>
    <button class="btn">Search</button>
    <div class="btn-group">
      <button class="btn dropdown-toggle" data-toggle="dropdown" tabindex="-1">Options <span class="caret"></span></button>
      <ul class="dropdown-menu">
          <li>
            <table class="table table-condensed">
              % for key, value in saved_searches.iteritems():
              <tr>
                <td>
                  <a tabindex="-1" href="${request.current_route_url()}?form=search&saved=${key}">${value[1]}</a>
                </td>
                <td width="20">
                  <a class="pull-right" tabindex="-1" href="${request.current_route_url()}?form=search&delete=${key}"><i class="icon-remove"></i></a>
                </td>
              </tr>
              % endfor
            </table>
          </li>
        <li class="divider"></li>
        <li><a tabindex="-1" href="#" data-toggle="modal" data-target="#savequerydialog">Save current search filter</a></li>
        <li><a tabindex="-1" href="${request.current_route_url()}?form=search&reset">Reset current search filter</a></li>
      </ul>
    </div>
    % if len(listing.search_filter) > 0:
      <span class="muted"><small>(${len(listing.search_filter)} filter applied)</small></span>
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
          ${", ".join(unicode(render_filter_link(v, field)) for v in value) | h}
        % else:
          ${render_filter_link(value, field)}
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

<div id="savequerydialog" class="modal hide fade">
  <form id="savequery" action="${request.current_route_url()}">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h3>Save current search filter</h3>
  </div>
  <div class="modal-body">
    <label for="save">Queryname</label>
    <input type="textfield" id="save" name="save"/>
    <input type="hidden" name="form" value="search"/>
    <p><small>Please insert a name for your query. It it will be selectable under
    this name in the options menu of the search after saving.</small></p>
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">Close</a>
    <input class="btn btn-primary" type="button" onclick="formSubmit()" value="Save Query">
  </div>
  </form>
</div>


<%def name="render_filter_link(value, field)">
  <a href="${request.current_route_url()}?form=search&search=${value | h}&field=${field[0]}" class="filter" title="${'Filter %s on %s in %s' % (clazz.get_item_modul().get_label(plural=True), value, field[1])}">${value | h}</a>
</%def>

<script type="text/javascript">
function openItem(url) {
  location.href = url;
};

function formSubmit() {
  document.getElementById("savequery").submit();
}

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
