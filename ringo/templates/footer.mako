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
    <div class="pull-right">
      <p class="muted credit">${h.get_app_title()} ver. ${h.get_app_version()}</p>
    </div>
  </div>
</div>
