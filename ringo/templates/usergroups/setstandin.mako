<%inherit file="/main.mako" />
<%namespace name="main" file="/main.mako"/>
<div class="page-header">
  <div class="row">
    <div class="col-sm-12">
      <h1>${_('Set standin for')}: ${user.profile[0]}</h1>
    </div>
  </div>
</div>
<div class="row">
  <div class="col-md-12">
    <div id="form">
      ${form}
    </div>
  </div>
</div>
