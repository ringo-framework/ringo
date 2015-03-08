<%
from ringo.lib.helpers import prettify
value = field.get_value() or []
if not isinstance(value, list):
  value = [value]
selected = [str(id) for id in value if id]
visible_items = []
hidden_items = []
for item in items:
  if item[2]:
    visible_items.append(item)
  else:
    hidden_items.append(item)


def render_item_link(request, clazz, permission, item, value, modal=False, backlink=True):
  out = []
  css_class = ["link"]
  # Only take the path of the url and ignore any previous search filters.
  url = request.route_path(h.get_action_routename(clazz, permission), id=item[0].id)
  if backlink:
    out.append('<a href="%s?backurl=%s" ' % (url, request.current_route_path()))
  else:
    out.append('<a href="%s" ' % (url))
  if modal:
    css_class.append("modalform")
  out.append('class="%s"' % " ".join(css_class))
  out.append('>')
  if hasattr(value, "render"):
    out.append('%s' % _(value.render()))
  else:
    out.append('%s' % _(value))
  out.append('</a>')
  return " ".join(out)
%>

% if field.renderer.showsearch == "true" and not field.is_readonly():
<table class="table table-condensed table-striped datatable-simple">
% else:
<table class="table table-condensed table-striped datatable-blank">
% endif
  <thead>
    % if not field.is_readonly() and not field.renderer.hideadd == "true" and s.has_permission("create", clazz, request) and h.get_item_modul(request, clazz).has_action("create"):
    <tr class="table-toolbar">
      <th colspan="${len(tableconfig.get_columns())+1}">
      <a href="#"
      onclick="addItem('${request.route_path(h.get_action_routename(clazz,
      "create"))}', '${field.name}', '${field.renderer.form}',
      '${field._form._item.id}', '${h.get_item_modul(request,
      pclazz).clazzpath}', '${field.renderer.backlink != 'false'}')"
      ><i class="glyphicon glyphicon-plus"></i></a>
      </th>
    </tr>
    % endif
    <tr>
    % if not field.is_readonly() and field.renderer.onlylinked != "true":
      <th width="20px">
        % if not field.renderer.multiple == "false":
          <input type="checkbox" name="check_all" onclick="checkAll('${field.name}');">
        % endif
      </th>
    % endif
      % for num, col in enumerate(tableconfig.get_columns()):
      <th class="${num > 0 and 'hidden-xs'}" width="${col.get('width')}">${_(col.get('label'))}</th>
      % endfor
    </tr>
  </thead>
  <tbody>
    % for item in items:
      <%
      permission = None
      if s.has_permission("update", item[0], request):
        permission = "update"
      elif s.has_permission("read", item[0], request):
        permission = "read"
      elif not field.renderer.showall == "true":
        continue
      %>
      <tr>
      % if not field.is_readonly() and field.renderer.onlylinked != "true":
        <td>
          % if not field.renderer.multiple == "false":
            % if str(item[0].id) in selected:
              <input type="checkbox" value="${item[0].id}" name="${field.name}" checked="checked" onclick="check('${field.name}', this);"/>
            % else:
              <input type="checkbox" value="${item[0].id}" name="${field.name}" onclick="check('${field.name}', this);"/>
            % endif
          % else:
            % if str(item[0].id) in selected:
              <input type="checkbox" value="${item[0].id}" name="${field.name}" onclick="checkOne('${field.name}', this);" checked="checked"/>
            % else:
              <input type="checkbox" value="${item[0].id}" name="${field.name}" onclick="checkOne('${field.name}', this);"/>
            % endif
          % endif
        </td>
      % endif
      % for num, col in enumerate(tableconfig.get_columns()):
        <%
          try:
            rvalue = prettify(request, item[0].get_value(col.get('name'), expand=col.get('expand')))
            if isinstance(rvalue, list):
              value = ", ".join(unicode(_(v)) for v in rvalue)
            else:
              value = rvalue
          except AttributeError:
            value = "NaF"
        %>
        <td class="${num > 0 and 'hidden-xs'}">
        % if permission and not field.renderer.nolinks == "true":
            ${render_item_link(request, clazz, permission, item, value,
                              (field.renderer.openmodal == "true"),
                              (field.renderer.backlink != "false"))}
          </a>
        % else:
          ${_(value)}
        % endif
        </td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
% for item in hidden_items:
  % if str(item[0].id) in selected:
    <input style="display:none" type="checkbox" value="${item[0].id}" name="${field.name}" checked="checked"/>
  % endif
% endfor

<script type="text/javascript">
function addItem(url, foreignkey, form, id, clazz, backlink) {
  //var activetab = $('.tab-pane.active');
  if (form == "None") {
    if (backlink == 'False') {
      location.href = url + '?addrelation=' + foreignkey + ':' + clazz + ':' + id;
    } else {
      location.href = url + '?addrelation=' + foreignkey + ':' + clazz + ':' + id + '&backurl=' + document.URL;
    }
  } else {
    if (backlink == 'False') {
      location.href = url + '?addrelation=' + foreignkey + ':' + clazz + ':' + id;
    } else {
      location.href = url + '?addrelation=' + foreignkey + ':' + clazz + ':' + id + '&form=' + form + '&backurl=' + document.URL;
    }
  }
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
  check(checkId);
}

function checkOne(checkId, element) {
  var inputs = document.getElementsByTagName("input");
  for (var i = 0; i < inputs.length; i++) {
      if (inputs[i].type == "checkbox" && inputs[i].name == checkId && inputs[i].value != element.value) {
        inputs[i].checked = false;
      }
  }
  check(checkId);
}

function check(checkId) {
  /* Will add a hidden checkbox with no value in case no other checkbox is
   * selected. This is needed to items with no selection, as in this case html
   * does not submit the checkbox field at all. So this is a hack to simulate
   * an empty selection */
  var inputs = $("input[type='checkbox'][name="+checkId+"]");
  var selected = inputs.filter(":checked");
  if (selected.length == 0 && inputs.length > 0) {
    $(inputs[0]).before('<input id="'+checkId+'-empty" style="display:none" type="checkbox" value="" name="'+checkId+'" checked="checked"/>');
  } else {
    $("#"+checkId+"-empty").remove();
  }
}
</script>
