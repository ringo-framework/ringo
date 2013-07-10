<%inherit file="/main.mako" />
<%namespace name="main" file="/main.mako"/>
<div class="row-fluid page-header">
  <div class="span6">
    <h1>${_('Read')} ${_(clazz.get_item_modul().get_label())}</h1>
  </div>
  <div class="span6">
    <div class="btn-toolbar pull-right">
      <div class="context-menu btn-group">
        <!-- Item specific actions -->
        ${main.render_item_specific_actions(item)}
      </div>
      <div class="context-menu btn-group">
        <!-- Base ringo actions -->
        ${main.render_item_base_actions(item)}
      </div>
    </div>
  </div>
</div>
<div class="row-fluid">
  <div class="span12">
    ${form | n}
  </div>
</div>
