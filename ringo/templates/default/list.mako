<%inherit file="/main.mako" />
<%namespace name="base" file="/base.mako"/>
<div class="page-header">
  <div class="row">
    <div class="col-sm-8">
      <h1>
        ${N_(h.get_item_modul(request, clazz).get_label(plural=True))}</h1>
    </div>
    <div class="col-sm-4 visible-xs">
      <div class="context-menu hidden-print">
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
      <div class="context-menu pull-right hidden-print">
        <div class="btn-toolbar">
          <div class="btn-group">
            <%
              actions = []
              for action in h.get_item_modul(request, clazz).actions:
                if (action.is_visible("overview")
                    and s.has_permission(action.get_permission(), request.context, request)):
                      actions.append(action)
            %>
            % if len(actions) > 0:
              ${render_link(actions[0], clazz, btn=True)}
              % if len(actions) > 1:
                <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>
                <ul class="dropdown-menu">
                  % for action in actions:
                  <li>
                    ${render_link(action, clazz)}
                  </li>
                  % endfor 
                </ul>
              % endif
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
<%def name="render_link(action, clazz, btn=False)">
  <%
    url = request.route_path(h.get_action_routename(clazz, action.name.lower()))
    if action.description:
      title = _('Add a new %s entry') % h.get_item_modul(request, clazz).get_label()
    elif action.name.lower() == "create":
      title = _('Add a new %s entry') % h.get_item_modul(request, clazz).get_label()
    elif action.name.lower() == "import":
      title = _('Import new %s entries') % h.get_item_modul(request, clazz).get_label()
    else: 
      title = action.name
    icon = base.get_icon(action)
    if action.name.lower() == "create":
      name = _('Add')
    elif action.name.lower() == "import":
      name = _('Import')
    else:
      name = action.name
    if btn:
      btn_css = "btn btn-primary"
    else:
      btn_css = ""
  %>
  <a href="${url}" title="${title}" class="${btn_css}"><i class="${icon}">&nbsp;</i>${name}</a>
</%def>
