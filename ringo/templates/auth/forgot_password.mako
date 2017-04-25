<%inherit file="/main.mako" />
<div class="page-header">
  <div class="row">
    <div class="col-md-12">
      <h1>${_('Reset Password')}</h1>
    </div>
  </div>
</div>
% if not complete:
<div class="row">
  <div class="col-md-12">
    <p>${_('Enter your Loginname and a password reset email will be sent out')}</p>
    <br>
    ${form}
  </div>
</div>
% else:
<div class="row">
  <div class="col-md-12">
    <p>${msg}</p>
  </div>
</div>
% endif
