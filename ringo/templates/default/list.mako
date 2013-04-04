<%inherit file="/main.mako" />
<div class="row-fluid page-header">
  <div class="span6">
    <h1>${N_(clazz.get_item_modul().get_label(plural=True))}</h1>
  </div>
  <div class="span6">
    <div class="pull-right context-menu btn-group">
      <a href="${request.route_url(clazz.get_action_routename('create'))}" class="btn btn-primary">New</a>
    </div>
  </div>
</div>
<div class="row-fluid">
  <div class="span12">
    ${listing | n}
  </div>
</div>
