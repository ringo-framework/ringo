<%inherit file="/main.mako" />
<%namespace name="main" file="/main.mako"/>
<div class="page-header">
  <div class="row">
    <div class="col-sm-8">
      <h1>${_(clazz.get_item_modul().get_label())}: ${item}</h1>
    </div>
    <div class="col-sm-4 visible-xs">
      <div class="context-menu">
        <div class="btn-toolbar">
          <div class="btn-group btn-group-justified">
            <!-- Item specific actions -->
            ${main.render_item_specific_actions(item)}
            <!-- Base ringo actions -->
            ${main.render_item_base_actions(item)}
          </div>
        </div>
      </div>
    </div>
    <div class="col-sm-4 hidden-xs">
      <div class="context-menu pull-right">
        <div class="btn-toolbar">
          <div class="btn-group">
            <!-- Item specific actions -->
            ${main.render_item_specific_actions(item)}
            <!-- Base ringo actions -->
            ${main.render_item_base_actions(item)}
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
<div class="row">
  <div class="col-md-12">
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
