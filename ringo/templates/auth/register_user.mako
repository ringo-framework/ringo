<%inherit file="/main.mako" />
<div class="page-header">
  <div class="row">
    <div class="col-md-12">
      <h1>${_('Register Account')}</h1>
    </div>
  </div>
</div>
<div class="row">
  <div class="col-md-12">
    <p>${_('Please fillout the form the register a new account. You will recieve an email with a confirmation link to complete the registration.')}</p>
    <br>
    ${form | n}
  </div>
</div>
