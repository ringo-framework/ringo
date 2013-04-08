<%inherit file="/main.mako" />
<div class="row-fluid page-header">
  <div class="span4">
  </div>
  <div class="span4">
    <div class="well">
      <h3>Login</h3>
      ${form | n}
      <ul>
        <li><a href="${request.route_url("register_user")}">${_('Register new user')}</a></li>
        <li><a href="${request.route_url("forgot_password")}">${_('Forgot password')}</a></li>
      </ul>
    </div>
  </div>
  <div class="span4">
  </div>
</div>
