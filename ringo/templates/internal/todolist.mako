<%
import datetime
from ringo.lib.helpers import format_datetime
%>
<table id="todolisting" class="table table-condensed table-striped table-bordered">
  <thead>
    <tr>
      % for field in tableconfig.get_columns():
      <th width="${field.get('width')}">${field.get('label')}</th>
      % endfor
      ##<th width="10"><span class="glyphicon glyphicon-check"></span></th>
    </tr>
  </thead>
  <tbody>
    % for item in items:
    <%
      url = None
      if s.has_permission("update", item, request):
        url = request.route_path(item.get_action_routename("update"), id=item.id)
      elif s.has_permission("read", item, request):
        url = request.route_path(item.get_action_routename("read"), id=item.id)
    %>
    <tr id="todoentry_${item.id}">
      % for field in tableconfig.get_columns():
      % if url:
      <td onclick="openItem('${url}')" class="link">
      % else:
      <td>
      % endif
          <%
            form_config = tableconfig.get_form_config()
            try:
              if field.get('expand'):
                value = item.get_value(field.get('name'))
              else:
                value = getattr(item, field.get('name'))
              if isinstance(value, datetime.datetime):
                value = format_datetime(value)
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
      ##<td>
      ##  % if s.has_permission("read", item, request):
      ##    <a href="#" class="linkmarkasdone"><span class="glyphicon glyphicon-check"></span></a>
      ##  % endif
      ##</td>
    </tr>
    % endfor
  </tbody>
</table>

<script>
var todolist = $('#todolisting').dataTable( {
       "bPaginate": true,
       "sPaginationType": "full_numbers",
       "bLengthChange": true,
       "bFilter": true,
       "bSort": true,
       /* Disable initial sort */
       "aaSorting": [],
       "bInfo": true,
       "bAutoWidth": true
 });

$('.linkmarkallasread').click( function () {
  $("#newslisting tbody tr").each(function(index) {
    var row = $(this);
    var id = $(row).attr("id").split("_")[1];
    markNewsAsRead(row, id);
  });
});

$('.linkmarkasdone').click( function () {
  var row = $(this).closest("tr").get(0);
  var id = $(row).attr("id").split("_")[1];
  markTodoAsDone(row, id);
});

function markTodoAsDone(row, id) {
  $.ajax({
    headers : {
      'Accept' : 'application/json',
      'Content-Type' : 'application/json'
    },
    url : '${request.host_url}/rest/todo/'+id+'/markasdone',
    type : 'PUT',
    success : function(response, textStatus, jqXhr) {
      /* TODO: Try to animate the deletion of the column. Tried to
      call the final deletion as a callback which does not work. (ti)
      <2014-01-30 12:35> */
      $('#todoentry_'+id).hide(1000);
      console.log("Todo successfully marked as done!");
    },
    error : function(jqXHR, textStatus, errorThrown) {
      // log the error to the console
      console.log("The following error occured: " + textStatus, errorThrown);
    },
    complete : function() {
      todolist.fnDeleteRow(row);
    }
  });
};
</script>
