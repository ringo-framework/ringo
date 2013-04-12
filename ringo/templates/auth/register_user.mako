<%inherit file="/main.mako" />
<div class="row-fluid page-header">
  <div class="span6">
    <h1>${_('Register Account')}</h1>
  </div>
</div>
<div class="row-fluid">
  <div class="span8">
    <p>${_('Please fillout the form the register a new account. You will recieve an email with a confirmation link to complete the registration.')}</p>
    <br>
    ${form | n}
  </div>
</div>
