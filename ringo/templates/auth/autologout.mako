<%inherit file="/main.mako" />
<div class="page-header">
<h1>Auto Logout</h1>
</div>
<p>${_('You have been automatically logged out because your session has expired. Please click on the link below to login into the application again.')}</p>
<p><a href="${request.route_path('login')}" class="btn btn-primary">${_('Login')}</a></p>
