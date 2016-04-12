<%inherit file="/main.mako" />
<div class="page-header">
  <div class="row">
    <div class="col-md-12">
      <h1>${_('Register Account')}</h1>
    </div>
  </div>
</div>
% if not complete:
<div class="row">
  <div class="col-md-12">
    <p>${_('Please fillout the form the register a new account. You will recieve an email with a confirmation link to complete the registration.')}</p>
    <br>
    ${form}
  </div>
</div>
% else:
<div class="row">
  <div class="col-md-12">
    <p>${_("User has been created and a confirmation mail was sent to the users email adress. Please check your email.")}</p>
  </div>
</div>
% endif
