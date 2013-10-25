<%inherit file="/main.mako" />
<div class="page-header">
  <div class="row">
    <div class="col-sm-8">
      <h1>${N_(clazz.get_item_modul().get_label(plural=True))}</h1>
    </div>
    <div class="col-sm-4 visible-xs">
      <div class="context-menu">
        <div class="btn-toolbar">
          <div class="btn-group btn-group-justified">
            % if clazz.get_item_modul().has_action('create'):
            <a href="${request.route_url(clazz.get_action_routename('create'))}" class="btn btn-primary btn-block">${_('New')}</a>
            % endif
          </div>
        </div>
      </div>
    </div>
    <div class="col-sm-4 hidden-xs">
      <div class="context-menu pull-right">
        <div class="btn-toolbar">
          <div class="btn-group">
            % if clazz.get_item_modul().has_action('create'):
            <a href="${request.route_url(clazz.get_action_routename('create'))}" class="btn btn-primary">${_('New')}</a>
            % endif
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
<div class="row">
  <div class="col-md-12">
    ${listing | n}
  </div>
</div>
