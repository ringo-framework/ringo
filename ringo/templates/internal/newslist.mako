<%
import datetime
from ringo.lib.helpers import format_datetime
%>
<table id="newslisting" class="table table-condensed table-striped table-bordered">
  <thead>
    <tr>
      % for field in tableconfig.get_columns():
      <th width="${field.get('width')}">${field.get('label')}</th>
      % endfor
      ##<th width="10"><a href="#" class="linkmarkallasread"><span class="glyphicon glyphicon-check"></span></a></th>
      <th width="10"><span class="glyphicon glyphicon-check"></span></th>
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
    <tr id="newsentry_${item.id}">
      % for field in tableconfig.get_columns():
      % if url:
      <td onclick="openItem('${url}')" class="link">
      % else:
      <td>
      % endif
          <%
            form_config = tableconfig.get_form_config()
            try:
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
      <td>
        % if s.has_permission("read", item, request):
          <a href="#" class="linkmarkasread"><span class="glyphicon glyphicon-check"></span></a></td>
        % endif
    </tr>
    % endfor
  </tbody>
</table>

<script>
var newslist = $('#newslisting').dataTable( {
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

$('.linkmarkasread').click( function () {
  var row = $(this).closest("tr").get(0);
  var id = $(row).attr("id").split("_")[1];
  markNewsAsRead(row, id);
});

function markNewsAsRead(row, id) {
  $.ajax({
    headers : {
      'Accept' : 'application/json',
      'Content-Type' : 'application/json'
    },
    url : '${request.host_url}/rest/news/'+id+'/markasread',
    type : 'PUT',
    success : function(response, textStatus, jqXhr) {
      /* TODO: Try to animate the deletion of the column. Tried to
      call the final deletion as a callback which does not work. (ti)
      <2014-01-30 12:35> */
      $('#newsentry_'+id).hide(1000);
      console.log("News successfully marked as read!");
    },
    error : function(jqXHR, textStatus, errorThrown) {
      // log the error to the console
      console.log("The following error occured: " + textStatus, errorThrown);
    },
    complete : function() {
      newslist.fnDeleteRow(row);
    }
  });
};
</script>
