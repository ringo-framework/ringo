<%inherit file="/main.mako" />
<div class="dialog modal hide fade" tabindex="-1">
  <div class="modal-header">
    <h3 id="myModalLabel">${_('Login')}</h3>
  </div>
  <div class="modal-body">
    <p>${form | n}</p>
    <ul>
      <li><a href="${request.route_url("register_user")}">${_('Register Account')}</a></li>
      <li><a href="${request.route_url("forgot_password")}">${_('Reset Password')}</a></li>
    </ul>
  </div>
</div>
