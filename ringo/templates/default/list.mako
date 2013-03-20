<%inherit file="/base.mako" />
<h1>List</h1>

<table class="table">
  % for item in items:
  <tr>
    <td>
      ${item}
    </td>
  </tr>
  % endfor
  % if len(items) == 0:
  <tr>
    <td>
    No items found
    </td>
  </tr>
  % endif

</table>

<a href="${request.route_url('admin-users-create')}" class="btn btn-primary">New</a>
