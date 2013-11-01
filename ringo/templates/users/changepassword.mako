<%inherit file="/main.mako" />
<%namespace name="main" file="/main.mako"/>
<div class="page-header">
  <div class="row">
    <div class="col-sm-12">
      <h1>${_('Change Password for')}: ${item}</h1>
    </div>
  </div>
</div>
<div class="row">
  <div class="col-md-12">
    <div id="form">
      ${form | n}
    </div>
  </div>
</div>
