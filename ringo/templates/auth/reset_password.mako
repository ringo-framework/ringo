<%inherit file="/main.mako" />
<div class="row-fluid page-header">
  <div class="span6">
    <h1>
    % if success:
      ${_('Password resetted')}
    % else:
      ${_('Password not resetted')}
    % endif
    </h1>
  </div>
</div>
<div class="row-fluid">
  <div class="span8">
    <p>${msg}</p>
    % if success:
      <p><a href="${request.route_url('login')}" class="btn btn-primary">${_('Login')}</a></p>
    % else:
      <p>
        <br>
        <a href="${request.route_url('forgot_password')}" class="btn btn-primary">${_('Try again')}</a>
        <a href="${request.route_url('login')}" class="btn btn-primary">${_('Login')}</a>
      </p>
    % endif
  </div>
</div>
