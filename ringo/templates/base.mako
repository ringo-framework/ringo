<!DOCTYPE html>

<html lang="en">
  <head>
    ##@TODO: Use title from configuration.
    <title>Ringo</title>
    <meta charset="utf-8">
    <meta content="width=device-width, initial-scale=1.0" name="viewport">
    <meta content="" name="description">
    <meta content="" name="author">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap -->
    <link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet" media="screen">
    <link href="/css/style.css" rel="stylesheet" media="screen">
    <style>
      ${h.get_formbar_css()}
    </style>

    <!-- HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
      <script src="../assets/js/html5shiv.js"></script>
    <![endif]-->

    <!-- Fav and touch icons -->
    <link href="../assets/ico/apple-touch-icon-144-precomposed.png" sizes="144x144" rel="apple-touch-icon-precomposed">
    <link href="../assets/ico/apple-touch-icon-114-precomposed.png" sizes="114x114" rel="apple-touch-icon-precomposed">
    <link href="../assets/ico/apple-touch-icon-72-precomposed.png" sizes="72x72" rel="apple-touch-icon-precomposed">
    <link href="../assets/ico/apple-touch-icon-57-precomposed.png" rel="apple-touch-icon-precomposed">
    <link href="../assets/ico/favicon.png" rel="shortcut icon">
  </head>

  <body>


    <!-- Part 1: Wrap all page content here -->
    <div id="wrap">

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
                <li class="${(modul == None) and 'active'}"><a href="#">Home</a></li>
                <li class="${(modul == 'modules') and 'active'}"><a href="${request.route_url('modules-list')}">Modules</a></li>
                <li class="${(modul == 'users') and 'active'}"><a href="${request.route_url('users-list')}">Users</a></li>
                <li class="${(modul == 'usergroups') and 'active'}"><a href="${request.route_url('usergroups-list')}">Usergroups</a></li>
                <li class="${(modul == 'roles') and 'active'}"><a href="${request.route_url('roles-list')}">Roles</a></li>
              </ul>
              <ul class="nav pull-right">
                <li class="divider-vertical"></li>
                % if request.user:
                  <li class="dropdown">
                    <a href="#" class="dropdown-toggle" data-toggle="dropdown">${request.user.login}<b class="caret"></b></a>
                    <ul class="dropdown-menu">
                      <li><a href="#"><img class="icon" src="/images/icons/16x16/profile.png"/>Profile</a></li>
                      <li class="divider"></li>
                      <li><a href="${request.route_url('logout')}"><img class="icon" src="/images/icons/16x16/system-log-out.png"/>Logout</a></li>
                    </ul>
                  </li>
                % else:
                  <li><a href="${request.route_url('login')}">Login</a></li>
                % endif
              </ul>
            </div><!--/.nav-collapse -->
          </div>
        </div>
      </div>

      <!-- Begin page content -->
      <div class="container">
        <div id="status-messages">
          ${self.flash_messages()}
        </div>
        ${next.body()}
      </div>

      <div id="push"></div>
    </div>

    <div id="footer">
      <div class="container">
        <p class="muted credit">Ringo ver. X.X</p>
      </div>
    </div>
    <script src="http://code.jquery.com/jquery.js"></script>
    <script src="/static/bootstrap/js/bootstrap.min.js"></script>
    <script src="/static/js/init.js"></script>
  </body>
</html>


## flash messages with css class und fade in options
<%def name="flash_messages()">
  % for message in request.session.pop_flash('success'):
    <div class="alert alert-success fade in">
      <button type="button" class="close" data-dismiss="alert">&times;</button>
      ${message}
    </div>
  % endfor
  % for message in request.session.pop_flash('error'):
    <div class="alert alert-error fade in">
      <button type="button" class="close" data-dismiss="alert">&times;</button>
      ${message}
    </div>
  % endfor
</%def>
