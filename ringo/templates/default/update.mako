<%inherit file="/base.mako" />
<div class="row-fluid pageheader">
  <div class="span6">
    <h1>Edit</h1>
  </div>
  <div class="span6">
    <div class="pull-right context-menu btn-group">
      <a href="/users/read/${item.id}" class="btn"><i class="icon-eye-open"></i></a>
      <a href="/users/delete${item.id}" class="btn"><i class="icon-trash"></i></a>
    </div>
  </div>
</div>
<div class="row-fluid">
  <div class="span12">
    ${form | n}
  </div>
</div>
