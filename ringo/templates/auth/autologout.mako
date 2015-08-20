<%inherit file="/main.mako" />
<div class="page-header">
  <h1>${_('Session expired')}</h1>
</div>
<p>${_('You have been automatically logged out because your session has expired.')}</p>
<p><a href="${request.route_path('login')}" class="btn btn-primary">${_('Re-Login')}</a></p>
