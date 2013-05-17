<%inherit file="/main.mako" />
<div class="row-fluid page-header">
  <div class="span6">
    <h1>${_('Reset Password')}</h1>
  </div>
</div>
<div class="row-fluid">
  <div class="span8">
    <p>${_('Enter your Loginname and a password reset email will be sent out')}</p>
    <br>
    ${form | n}
  </div>
</div>
