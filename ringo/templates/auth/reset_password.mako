<%inherit file="/main.mako" />
<div class="page-header">
  <div class="row">
    <div class="col-md-8">
      <h1>
      % if success:
        ${_('Password resetted')}
      % else:
        ${_('Password not resetted')}
      % endif
      </h1>
    </div>
  </div>
</div>
<div class="row">
  <div class="col-md-8">
    <p>${msg}</p>
    % if success:
      <p><a href="${request.route_path('login')}" class="btn btn-primary">${_('Login')}</a></p>
    % else:
      <p>
        <br>
        <a href="${request.route_path('forgot_password')}" class="btn btn-primary">${_('Try again')}</a>
        <a href="${request.route_path('login')}" class="btn btn-primary">${_('Login')}</a>
      </p>
    % endif
  </div>
</div>
