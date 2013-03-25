<!DOCTYPE html>
<html>
  <head>
    ##@TODO: Use title from configuration.
    <title>Ringo</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap -->
    <link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet" media="screen">
    <link href="/css/style.css" rel="stylesheet" media="screen">
    <style>
      ${h.get_formbar_css()}
    </style>
  </head>
  <body>
    <div class="navbar navbar-inverse navbar-fixed-top">
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
              <li class="active"><a href="#">Home</a></li>
              <li><a href="${request.route_url('users-list')}">Users</a></li>
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
    <div class="container">
    ${self.flash_messages()}
    ${next.body()}
    </div>
    <script src="http://code.jquery.com/jquery.js"></script>
    <script src="/static/bootstrap/js/bootstrap.min.js"></script>
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
