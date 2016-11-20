<%inherit file="/main.mako" />
<%namespace name="main" file="/main.mako"/>
<div class="page-header">
  <div class="row">
    <div class="col-sm-7">
      <h1 style="float:left">
        % if request.registry.settings.get("layout.show_modulname") != "false":
          ${_(h.get_item_modul(request, clazz).get_label())}:
        % endif
        ${item.render(request)}
      </h1>
        % if request.url.find("read") >= 0:
        <span class="badge hidden-print" style="float:left; margin-left:5px; margin-top:5px">
          <i class="fa fa-lock"></i> 
        </span> 
        % endif
    </div>
    % if s.has_role(request.user, "admin") or request.registry.settings.get("layout.show_contextmenu", "true") == "true":
      <div class="col-sm-5">
        <div class="context-menu pull-right">
          <div class="btn-toolbar">
            <div class="btn-group">
              <!-- Base ringo actions -->
              ${main.render_item_base_actions(item)}
            </div>
          </div>
        </div>
      </div>
    % endif
  </div>
</div>
<div class="row">
  <div class="col-md-12">
    ${form}
  </div>
</div>
