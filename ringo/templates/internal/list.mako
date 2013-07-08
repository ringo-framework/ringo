<div class="well well-small search-widget">
  <form name="search" class="form-inline" action="${request.current_route_url()}" method="POST">
    <input name="form" type="hidden" value="search">
    <input name="search" type="text" class="input-large" value="${search}" placeholder="Search for (Regexpr) in ..."/>
    <select name="field" class="input-small">
      <option value="">All fields</option>
      % for field in tableconfig.get_columns():
        % if field.get('name') == search_field:
          <option value="${field.get('name')}" selected>${field.get('label')}</option>
        % else:
          <option value="${field.get('name')}">${field.get('label')}</option>
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
  % for field in tableconfig.get_columns():
    <th width="${field.get('width')}">
      % if request.session['%s.list.sort_order' % clazz.__tablename__] == "asc":
        <a href="${request.current_route_url()}?sort_field=${field.get('name')}&sort_order=desc">${field.get('label')}</a>
      % else:
        <a href="${request.current_route_url()}?sort_field=${field.get('name')}&sort_order=asc">${field.get('label')}</a>
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
            ## TODO: Move this code into the baselist? As long as the
            ## expandation is only done on rendering the table things like
            ## searching or sorting will behavei odd as this is still done
            ## on the unexpanded values.
            raw_value = getattr(item, field.get('name'))
            value = raw_value
            if field.get('expand'):
              form_field = form_config.get_field(field.get('name'))
              for option in form_field.options:
                if option[1] == value:
                  value = option[0]
                  break
          except AttributeError:
            raw_value = "NaF"
        %>
        ## Escape value here
        % if isinstance(raw_value, list):
          ${", ".join(unicode(render_filter_link(raw_value, v, field)) for v in value) | h}
        % else:
          ${render_filter_link(raw_value, value, field)}
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


<%def name="render_filter_link(raw_value, value, field)">
  <a href="${request.current_route_url()}?form=search&search=${raw_value | h}&field=${field.get('name')}" class="filter" title="${'Filter %s on %s in %s' % (clazz.get_item_modul().get_label(plural=True), value, field.get('label'))}">${value | h}</a>
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
