<!-- Fixed navbar -->
<div class="navbar navbar-fixed-top">
  <div class="navbar-inner">
    <div class="container">
      <button type="button" class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
      <a class="brand" href="#">Ringo</a>
      <div class="nav-collapse collapse">
        <ul class="nav">
          <%
            if clazz:
              modul = clazz.get_item_modul().name
            else:
              modul = None
          %>
          <li class="${(modul == None) and 'active'}"><a href="#">${_('Home')}</a></li>
          <li class="${(modul == 'modules') and 'active'}"><a href="${request.route_url('modules-list')}">${_('Modules')}</a></li>
          <li class="${(modul == 'users') and 'active'}"><a href="${request.route_url('users-list')}">${_('Users')}</a></li>
          <li class="${(modul == 'usergroups') and 'active'}"><a href="${request.route_url('usergroups-list')}">${_('Usergroups')}</a></li>
          <li class="${(modul == 'roles') and 'active'}"><a href="${request.route_url('roles-list')}">${_('Roles')}</a></li>
        </ul>
        <ul class="nav pull-right">
          <li class="divider-vertical"></li>
          % if request.user:
            <li class="dropdown">
              <a href="#" class="dropdown-toggle" data-toggle="dropdown">${request.user.login}<b class="caret"></b></a>
              <ul class="dropdown-menu">
                <li><a href="${request.route_url('profiles-read', id=request.user.profile[0].id)}"><img class="icon" src="/images/icons/16x16/profile.png"/>${_('Profile')}</a></li>
                <li class="divider"></li>
                <li><a href="${request.route_url('logout')}"><img class="icon" src="/images/icons/16x16/system-log-out.png"/>${_('Logout')}</a></li>
              </ul>
            </li>
          % else:
            <li><a href="${request.route_url('login')}">${_('Login')}</a></li>
          % endif
        </ul>
      </div><!--/.nav-collapse -->
    </div>
  </div>
</div>
