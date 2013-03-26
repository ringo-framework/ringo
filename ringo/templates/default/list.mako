<%inherit file="/base.mako" />
<div class="row-fluid pageheader">
  <div class="span6">
    <h1>List</h1>
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
