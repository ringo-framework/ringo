<%inherit file="/main.mako" />
<div class="page-header">
  <div class="row">
    <div class="col-sm-8">
      <h1>
        ${N_(h.get_item_modul(request, clazz).get_label(plural=True))}</h1>
    </div>
    <div class="col-sm-4 visible-xs">
      <div class="context-menu">
        <div class="btn-toolbar">
          <div class="btn-group btn-group-justified">
            % if h.get_item_modul(request, clazz).has_action('create'):
              % if h.get_item_modul(request, clazz).get_action('create').display != 'hide':
                <a href="${request.route_path(h.get_action_routename(clazz,
                  'create'))}" class="btn btn-primary btn-block" title="${_('Add a new %s entry' % h.get_item_modul(request, clazz).get_label())}">${_('New')}
                  </a>
              % endif
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
              show_create =  h.get_item_modul(request, clazz).has_action('create') and h.get_item_modul(request, clazz).get_action('create').is_visible("overview") and s.has_permission('create', request.context, request)
              show_import =  h.get_item_modul(request, clazz).has_action('import') and h.get_item_modul(request, clazz).get_action('import').is_visible("overview") and s.has_permission('import', request.context, request)
            %>
            % if show_create:
              <a href="${request.route_path(h.get_action_routename(clazz, 'create'))}" title="${_('Add a new %s entry') % h.get_item_modul(request, clazz).get_label()}" class="btn btn-primary"><i class="glyphicon glyphicon-plus">&nbsp;</i>${_('New')}</a>
            % elif show_import:
              <a href="${request.route_path(h.get_action_routename(clazz, 'import'))}" title="${_('Import new %s entries') % h.get_item_modul(request, clazz).get_label()}" class="btn btn-primary"><i class="glyphicon glyphicon-import">&nbsp;</i>${_('New')}</a>
            % endif
            % if show_create and show_import:
              <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>
              <ul class="dropdown-menu">
                % if show_create:
                <li>
                  <a href="${request.route_path(h.get_action_routename(clazz, 'create'))}" title="${_('Add a new %s entry') % h.get_item_modul(request, clazz).get_label()}"><i class="glyphicon glyphicon-plus">&nbsp;</i>${_('Create')}</a>
                </li>
                % endif
                % if show_import:
                <li>
                  <a href="${request.route_path(h.get_action_routename(clazz, 'import'))}" title="${_('Import new %s entries') % h.get_item_modul(request, clazz).get_label()}"><i class="glyphicon glyphicon-import">&nbsp;</i>${_('Import')}</a>
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
    ${listing}
  </div>
</div>
