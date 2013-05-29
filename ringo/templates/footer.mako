<div class="container">
  <div class="navbar">
    % if request.user and s.has_role(request.user, 'admin'):
    <ul class="nav">
      <li class="dropdown dropup">
        <a href="#" data-toggle="dropdown"><img src="${request.static_url('ringo:static/images/icons/16x16/applications-system.png')}"/>${_('Administration')}<b class="caret"></b></a>
        <ul class="dropdown-menu dropup-menu" role="menu">
          <li class="${(modul == 'modules') and 'active'}"><a href="${request.route_url('modules-list')}">${_('Modules')}</a></li>
          ##<li class="${(modul == 'actions') and 'active'}"><a href="${request.route_url('actions-list')}">${_('Actions')}</a></li>
          <li class="${(modul == 'users') and 'active'}"><a href="${request.route_url('users-list')}">${_('Users')}</a></li>
          <li class="${(modul == 'usergroups') and 'active'}"><a href="${request.route_url('usergroups-list')}">${_('Usergroups')}</a></li>
          <li class="${(modul == 'roles') and 'active'}"><a href="${request.route_url('roles-list')}">${_('Roles')}</a></li>
        </ul>
      </li>
    </ul>
    % endif
    <ul class="nav pull-right">
      <li>
        <a href="${request.route_url('about')}">${_('About')}</a>
      </li>
      <li>
        <a href="${request.route_url('contact')}">${_('Contact')}</a>
      </li>
      <li>
        <a href="${request.route_url('version')}" title="${_('Show version information')}">${h.get_app_title()} ver. ${h.get_app_version()}</a>
      </li>
    </ul>
  </div>
</div>
