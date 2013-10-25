<%inherit file="/main.mako" />
<div class="page-header">
  <div class="row">
    <div class="col-md-12">
      <h1>${_('Reset Password')}</h1>
    </div>
  </div>
</div>
<div class="row">
  <div class="col-md-12">
    <p>${_('Enter your Loginname and a password reset email will be sent out')}</p>
    <br>
    ${form | n}
  </div>
</div>
