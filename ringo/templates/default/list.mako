<%inherit file="/base.mako" />
<h1>List</h1>
${listing | n}
<a href="${request.route_url('users-create')}" class="btn btn-primary">New</a>
