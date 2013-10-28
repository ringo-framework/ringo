<%inherit file="/main.mako" />
<div class="dialog modal fade" id="myModal">
  <div class="modal-dialog">
    <div class="panel panel-primary">
      <div class="panel-heading">${_('Login')}</div>
        <div class="panel-body">
          <p>${form | n}</p>
          <p>${_('If you forgot your password or do not have a account yet please select one of the following options:')}</p>
          <ul class="list-unstyled">
            % if mailer_enabled:
            <li><a href="${request.route_url("register_user")}">${_('Register Account')}</a></li>
            <li><a href="${request.route_url("forgot_password")}">${_('Reset Password')}</a></li>
            % endif
          </ul>
        </div>
      </div>
    </div>
  </div>
</div>
