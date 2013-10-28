<table class="table table-condensed table-striped table-bordered datatable-blank">
  <thead>
    % if not field.is_readonly():
    <tr class="table-toolbar">
      <th colspan="${len(tableconfig.get_columns())+1}">
      <a href="#"
      onclick="addItem('${request.route_url(clazz.get_action_routename("create"))}', '${field.renderer.foreignkey}', '${field.renderer.form}', '${field._form._item.id}')"
      class="btn btn-default btn-small">${_('Add')}</a>
      </th>
    </tr>
    % endif
    <tr>
    % if not field.is_readonly() and not field.renderer.onlylinked == "true":
      <th width="20px">
        <input type="checkbox" name="check_all" onclick="checkAll('${field.name}');">
      </th>
    % endif
      % for num, col in enumerate(tableconfig.get_columns()):
      <th class="${num > 0 and 'hidden-xs'}" width="${col.get('width')}">${col.get('label')}</th>
      % endfor
    </tr>
  </thead>
  <tbody>
    % for item in items:
    <tr>
      % if not field.is_readonly() and not field.renderer.onlylinked == "true":
        <td>
          <input type="checkbox" value="${item.id}" name="${field.name}"/>
        </td>
      % else:
          ## Render a hidden checkbox field as we need to submit the values in
          <input style="display:none" type="checkbox" value="${item.id}" name="${field.name}"/>
      % endif
      % for num, col in enumerate(tableconfig.get_columns()):
        % if s.has_permission("update", item, request):
          <td class="${num > 0 and 'hidden-xs'}"
          onclick="openItem('${request.route_url(clazz.get_action_routename("update"), id=item.id)}')">
        % else:
          <td class="${num > 0 and 'hidden-xs'}" onclick="openItem('${request.route_url(clazz.get_action_routename("read"), id=item.id)}')">
        % endif 
          <%
            form_config = tableconfig.get_form_config()
            try:
              value = item.get_value(col.get('name'))
            except AttributeError:
              value = "NaF"
          %>
          ## Escape value here
          % if isinstance(value, list):
            ${", ".join(unicode(v) for v in value) | h}
          % else:
            ${value}
          % endif
      </td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>

<script type="text/javascript">
function openItem(url) {
  //var activetab = $('.tab-pane.active');
  location.href = url + '?backurl=' + document.URL;
};

function addItem(url, foreignkey, form, id) {
  //var activetab = $('.tab-pane.active');
  location.href = url + '?values=' + foreignkey + ':' + id + '&form=' + form + '&backurl=' + document.URL;
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
