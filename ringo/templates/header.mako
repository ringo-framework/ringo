<!-- Fixed navbar -->
<div class="navbar navbar-fixed-top">
  <div class="navbar-inner">
    <div class="container">
      <button type="button" class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
      <a class="brand" href="#">${h.get_app_title()}</a>
      <div class="nav-collapse collapse">
        <ul class="nav">
          <%
            if clazz:
              modul_name = clazz.get_item_modul().name
            else:
              modul_name = None
          %>
          <li class="${(modul_name == None) and 'active'}"><a href="${request.route_url('home')}">${_('Home')}</a></li>
          % for modul in h.get_modules(request, 'header-menu'):
            <li class="${(modul_name == modul.name) and 'active'}"><a
            href="${request.route_url(modul.name+'-list')}">${modul.get_label(plural=True)}</a></li>
          % endfor
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
