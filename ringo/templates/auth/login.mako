<%inherit file="/main.mako" />
<div class="dialog modal fade" id="myModal">
  <div class="modal-dialog">
    <div class="panel panel-primary">
      <div class="panel-heading">${_('Login')}</div>
        <div class="panel-body">
          <p>${form | n}</p>
          <small>
          % if registration_enabled:
          <p>${_('New here? Register a new account!')}<br>
          <a href="${request.route_path("register_user")}">${_('Register Account')}</a>
          </p>
          % endif
          % if pwreminder_enabled:
          <p>${_('Forgot your password? Reset your password here.')}<br>
          <a href="${request.route_path("forgot_password")}">${_('Reset Password')}</a>
          </p>
          % endif
          </small>
        </div>
      </div>
    </div>
  </div>
</div>
