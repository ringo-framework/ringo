<%inherit file="/main.mako" />
<div class="page-header">
  <div class="row">
    <div class="col-sm-8">
      <h1>${len(itemlist.items)} ${N_(clazz.get_item_modul().get_label(plural=True))}</h1>
    </div>
    <div class="col-sm-4 visible-xs">
      <div class="context-menu">
        <div class="btn-toolbar">
          <div class="btn-group btn-group-justified">
            % if clazz.get_item_modul().has_action('create'):
            <a href="${request.route_path(clazz.get_action_routename('create'))}" class="btn btn-primary btn-block">${_('New')}</a>
            % endif
          </div>
        </div>
      </div>
    </div>
    <div class="col-sm-4 hidden-xs">
      <div class="context-menu pull-right">
        <div class="btn-toolbar">
          <div class="btn-group">
            <%
              show_create =  clazz.get_item_modul().has_action('create') and s.has_permission('create', request.context, request)
              show_import =  clazz.get_item_modul().has_action('import') and s.has_permission('import', request.context, request)
            %>
            % if show_create:
              <a href="${request.route_path(clazz.get_action_routename('create'))}" class="btn btn-primary"><i class="glyphicon glyphicon-plus">&nbsp;</i>${_('New')}</a>
            % elif show_import:
              <a href="${request.route_path(clazz.get_action_routename('import'))}" class="btn btn-primary"><i class="glyphicon glyphicon-import">&nbsp;</i>${_('New')}</a>
            % endif
            % if show_create and show_import:
              <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>
              <ul class="dropdown-menu">
                % if show_create:
                <li>
                  <a href="${request.route_path(clazz.get_action_routename('create'))}"><i class="glyphicon glyphicon-plus">&nbsp;</i>${_('Create')}</a>
                </li>
                % endif
                % if show_import:
                <li>
                  <a href="${request.route_path(clazz.get_action_routename('import'))}"><i class="glyphicon glyphicon-import">&nbsp;</i>${_('Import')}</a>
                </li>
                % endif
              </ul>
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
