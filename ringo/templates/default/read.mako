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
    <ul class="nav nav-tabs">
      <li class="active"><a href="#form" data-toggle="tab">${_(clazz.get_item_modul().get_label())}</a></li>
      % if owner:
        <li><a href="#ownership" data-toggle="tab">${_('Owner')}</a></li>
      % endif
    </ul>
    <div class="tab-content">
      <div class="tab-pane active" id="form">
        ${form | n}
      </div>
      % if owner:
        <div class="tab-pane" id="ownership">
          ${owner| n}
        </div>
      % endif
    </div>
  </div>
</div>
