# -*- coding: utf8 -*-
<%inherit file="/main.mako" />
<%namespace name="main" file="/main.mako"/>
<div class="page-header">
  <div class="row">
    <div class="col-sm-12">
      <h1>${_('Remove account of')}: ${item}</h1>
    </div>
  </div>
</div>
<div class="row">
  <div class="col-md-12">
    <p>
      ${_('Here you can delete your account completely. When deleting all data of this account will be deleted too. This includes all the records that belong to that account. Next the deletion of the account may result in other users can not access records anymore.')}
    </p>
    <p>
      ${_('Please note that deleting your user account can not be undone.')}
      <!---->
    </p>
    <div id="form">
      ${form}
    </div>
  </div>
</div>
