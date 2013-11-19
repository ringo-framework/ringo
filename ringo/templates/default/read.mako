<%inherit file="/main.mako" />
<%namespace name="main" file="/main.mako"/>
<div class="page-header">
  <div class="row">
    <div class="col-sm-7">
      <h1>${_(clazz.get_item_modul().get_label())}: ${item}</h1>
    </div>
    <div class="col-sm-5 visible-xs">
      <div class="context-menu">
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
    <div class="col-sm-5 hidden-xs">
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
    <div class="main-pane active" id="form">
      ${form | n}
    </div>
    % if owner:
      <div class="main-pane" id="ownership">
        ${owner| n}
      </div>
    % endif
    % if logbook:
      <div class="main-pane" id="logbook">
        ${logbook| n}
      </div>
    % endif
  </div>
</div>
