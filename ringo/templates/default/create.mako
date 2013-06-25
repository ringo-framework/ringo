<%inherit file="/main.mako" />
<div class="row-fluid page-header">
  <div class="span6">
    <h1>${_('New')} ${clazz.get_item_modul().get_label(plural)}</h1>
  </div>
  <div class="span6">
  </div>
</div>
<div class="row-fluid">
  <div class="span12">
    ${form | n}
  </div>
</div>
