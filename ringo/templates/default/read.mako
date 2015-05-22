<%inherit file="/main.mako" />
<%namespace name="main" file="/main.mako"/>
<div class="page-header">
  <div class="row">
    <div class="col-sm-7">
      <h1 style="float:left">
        ${_(h.get_item_modul(request, clazz).get_label())}: ${item}
      </h1>
        <span class="badge" style="float:left; margin-left:5px; margin-top:5px">
          % if request.url.find("read") >= 0:
            <i class="fa fa-lock"></i> 
          % else:
            <i class="fa fa-unlock-alt"></i> 
          % endif
        </span> 
    </div>
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
  </div>
</div>
<div class="row">
  <div class="col-md-12">
    ${form}
  </div>
</div>
