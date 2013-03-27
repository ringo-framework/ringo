<%inherit file="/base.mako" />
<div class="row-fluid pageheader">
  <div class="span6">
    <h1>Read ${clazz.get_item_modul().get_label()}</h1>
  </div>
  <div class="span6">
    <div class="pull-right context-menu btn-group">
      <a href="${h.get_action_url(request, item, 'update')}" class="btn"><i class="icon-edit"></i></a>
      <a href="${h.get_action_url(request, item, 'delete')}" class="btn"><i class="icon-trash"></i></a>
    </div>
  </div>
</div>
<div class="row-fluid">
  <div class="span12">
    ${form | n}
  </div>
</div>
