<%
mode = h.get_app_mode(request) 
%>
<%namespace name="base" file="base.mako"/>
<div id="status-messages">
  ${base.flash_messages()}
</div>
% if mode:
  <div style="background-color: ${mode[2]};">
    <div class="container">
      <div id="mode" class="row">
        <div class="col-md-2">
          <center>
            <strong>[${mode[0]}]</strong>
          </center>
        </div>
        <div class="col-md-8">
          <center>
            % if mode[1]:
              ${mode[1]}
            % endif
            % if request._active_testcase:
              Testcase Active (<a href="${request.route_path("stop_test_case")}">Rollback</a>)
            % else:
              Testcase Inactice (<a href="${request.route_path("start_test_case")}">Start</a>)
            % endif
          </center>
        </div>
        <div class="col-md-2">
          <center>
            <strong>[${mode[0]}]</strong>
          </center>
        </div>
      </div>
    </div>
  </div>
% endif
<%include file="logo.mako" />
<div class="navbar navbar-default navbar-static-top">
  <div class="container">
    <div class="navbar-header">
      <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
      <a class="navbar-brand" href="${request.route_path('home')}">${h.get_app_title()}</a>
    </div>
    <div class="navbar-collapse collapse">
      <ul class="nav navbar-nav">
        <%
          if clazz:
            modul_name = h.get_item_modul(request, clazz).name
          else:
            modul_name = None
        %>
        % if request.user:
        <li class="${(modul_name == None) and 'active'}"><a href="${request.route_path('home')}">${_('Home')}</a></li>
        % endif
        % for modul in h.get_modules(request, 'header-menu'):
          <li class="${(modul_name == modul.name) and 'active'}"><a href="${request.route_path(modul.name+'-list')}">${modul.get_label(plural=True)}</a></li>
        % endfor
      </ul>
      <ul class="nav navbar-nav navbar-right">
        % if request.user:
        <li>
        % if request.registry.settings.get("layout.show_sessiontimer") == "true":
          <%include file="/sessiontimer.mako" />
        % endif
        </li>
        <li class="divider-vertical"></li>
          <li class="dropdown">
            <a href="#" class="dropdown-toggle" data-toggle="dropdown"><i class="fa fa-user"></i> ${request.user.profile[0].first_name} ${request.user.profile[0].last_name} (${request.user.login})<b class="caret"></b></a>
            <ul class="dropdown-menu">
              <li role="presentation" class="dropdown-header">${_('Settings')}</li>
              <li><a href="${request.route_path('profiles-update', id=request.user.profile[0].id)}"><img class="icon" src="${request.static_path('ringo:static/images/icons/16x16/profile.png')}"/>${_('Profile')}</a></li>
              <li><a href="${request.route_path('users-changepassword', id=request.user.id)}"><img class="icon" src="${request.static_path('ringo:static/images/icons/16x16/application-certificate.png')}"/>${_('Change Password')}</a></li>
              <li><a href="${request.route_path('usergroups-setstandin', id=request.user.default_gid)}"><img class="icon" src="${request.static_path('ringo:static/images/icons/16x16/system-users.png')}"/>${_('Set standin')}</a></li> 
              <li class="divider"></li>
              <% user_menu_modules = h.get_modules(request, 'user-menu') %>
                % if len(user_menu_modules) > 0:
                <li role="presentation" class="dropdown-header">${_('Service')}</li>
                ## Render entries for the user-menue
                % for modul in h.get_modules(request, 'user-menu'):
                  <li><a href="${request.route_path(modul.name+'-list')}">${_(modul.get_label(plural=True))}</a></li>
                % endfor
                <li class="divider"></li>
              % endif
              <li><a href="${request.route_path('logout')}"><img class="icon" src="${request.static_path('ringo:static/images/icons/16x16/system-log-out.png')}"/>${_('Logout')}</a></li>
            </ul>
          </li>
        % else:
          <li><a href="${request.route_path('login')}">${_('Login')}</a></li>
        % endif
      </ul>
    </div><!--/.nav-collapse -->
  </div>
</div>
