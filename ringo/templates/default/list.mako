<%inherit file="/main.mako" />
<div class="row-fluid page-header">
  <div class="span6">
    <h1>${N_(clazz.get_item_modul().get_label(plural=True))}</h1>
  </div>
  <div class="span6">
    <div class="pull-right context-menu btn-group">
      % if clazz.get_item_modul().has_action('create'):
      <a href="${request.route_url(clazz.get_action_routename('create'))}" class="btn btn-primary">${_('New')}</a>
      % endif
    </div>
  </div>
</div>
<div class="row-fluid">
  <div class="span12">
    ${listing | n}
  </div>
</div>
