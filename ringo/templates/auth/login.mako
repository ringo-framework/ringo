<%inherit file="/main.mako" />
<div class="panel panel-primary">
  <div class="panel-heading">${_('Login')}</div>
  <div class="panel-body">
    <p>${form | n}</p>
    <ul>
      <li><a href="${request.route_url("register_user")}">${_('Register Account')}</a></li>
      <li><a href="${request.route_url("forgot_password")}">${_('Reset Password')}</a></li>
    </ul>
  </div>
</div>
