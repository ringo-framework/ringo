<!DOCTYPE html>
<html lang="en">
  <head>
    <title>${h.get_app_title()}</title>
    <meta charset="utf-8">
    <meta content="width=device-width, initial-scale=1.0" name="viewport">
    <meta content="" name="description">
    <meta content="" name="author">
    <meta content="${client_language}" name="client_language">
    <meta content="${application_path}" name="application_path">
    <meta content="${s.get_auth_timeout(request.registry.settings)}" name="auth_timeout">
    <meta content="${s.get_auth_timeout_warning(request.registry.settings)}" name="auth_warning">
    <meta content="${request.route_path("autologout")}" name="auth_logout">
    <meta content="${request.route_path("keepalive")}" name="auth_keepalive">
    <meta content="${request.user}" name="auth_user">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap -->
    <link href="${request.static_path('ringo:static/bootstrap/css/bootstrap.min.css')}" rel="stylesheet" media="screen">
    <link href="${request.static_path('ringo:static/bootstrap/css/bootstrap-theme.min.css')}" rel="stylesheet" media="screen">
    % for filename in formbar_css_filenames: 
      <link href="${request.static_path('formbar:static/%s' % filename)}" rel="stylesheet" media="screen">
    % endfor
    <link href="${request.static_path('ringo:static/css/layout.css')}" rel="stylesheet" media="screen">
    <link href="${request.static_path('ringo:static/css/widgets.css')}" rel="stylesheet" media="screen">
    <link href="${request.static_path('ringo:static/css/style.css')}" rel="stylesheet" media="screen">
    <link href="${request.static_path('ringo:static/css/jquery-ui.min.css')}" rel="stylesheet" media="screen">
    <link href="${request.static_path('ringo:static/font-awesome/css/font-awesome.min.css')}" rel="stylesheet">

    <!-- HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
      <script src="../assets/js/html5shiv.js"></script>
    <![endif]-->

    <!-- Fav and touch icons -->
    <script src="${request.static_path('ringo:static/js/jquery.js')}"></script>
    <script src="${request.static_path('ringo:static/js/jquery-ui.js')}"></script>
    <script src="${request.static_path('ringo:static/js/spin.min.js')}"></script>
    <script src="${request.static_path('ringo:static/js/jquery.spin.js')}"></script>
    <script src="${request.static_path('ringo:static/js/moment.min.js')}"></script>
    <script src="${request.static_path('ringo:static/bootstrap/js/bootstrap.min.js')}"></script>
    <script src="${request.static_path('ringo:static/js/datatables/dataTables.js')}"></script>
    <script src="${request.static_path('ringo:static/js/datatables/datetime-moment.js')}"></script>
    <script src="${request.static_path('ringo:static/js/jquery.jcountdown.min.js')}"></script>
    <script src="${request.static_path('ringo:static/js/jquery.timer.js')}"></script>
    % for filename in formbar_js_filenames: 
      <script src="${request.static_path('formbar:static/%s' % filename)}"></script>
    % endfor
    <script src="${request.static_path('ringo:static/js/listfield.js')}"></script>
    <script src="${request.static_path('ringo:static/js/helpers.js')}"></script>
    <%include file="/favicons.mako" />
    <%include file="/custom-header.mako" />
  </head>
  <body>
  ${next.body()}
  <script>
    function openItem(url) {
      location.href = url;
    };
    function checkAll(checkId) {
      var inputs = document.getElementsByTagName("input");
      for (var i = 0; i < inputs.length; i++) {
          if (inputs[i].type == "checkbox" && inputs[i].name == checkId) {
              if(inputs[i].checked == true) {
                  inputs[i].checked = false ;
              } else if (inputs[i].checked == false ) {
                  inputs[i].checked = true ;
              }
          }
      }
    };
  </script>
  <script src="${request.static_path('ringo:static/js/ringo/autologout.js')}"></script>
  <script src="${request.static_path('ringo:static/js/init.js')}"></script>
  % if request.user:
  <div class="modal fade" id="logoutWarning">
    <div class="modal-dialog">
      <div class="panel panel-warning">
        <div class="panel-heading"><strong>${_('Logout will happen soon')}</strong></div>
        <div class="panel-body">
          <p>${_('Your session will expire soon because of inactivity. Click on "Renew session" to continue work and renew your session. Otherwise you will be logged out automatically shortly and all unsaved data will get lost.')}</p>
        </div>
        <div class="panel-footer">
          <a href="#" class="btn btn-default" id="logoutWarningOK">${_('Renew session')}</a>
        </div>
      </div>
    </div>
  </div>
  <div class="modal fade" id="DirtyFormWarning">
    <div class="modal-dialog">
      <div class="panel panel-warning">
        <div class="panel-heading"><strong>${_('Form contains unsaved changes!')}</strong></div>
        <div class="panel-body">
          <p>${_('Do you want to leave the current form without saving the changes? The changes will be lost if you do not save the data first!')}</p>
        </div>
        <div class="panel-footer">
          <a id="DirtyFormWarningCancelButton" class="btn btn-default" href="">${_('Stay in Form')}</a>
          <a id="DirtyFormWarningProceedButton" class="btn btn-warning" href="">${_('Leave the Form')}</a>

        </div>
      </div>
    </div>
  </div>
  % endif
  <div class="modal fade" id="modalform">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
          <h4 class="modal-title">Modal title</h4>
        </div>
        <div class="modal-body">
          <p>One fine body&hellip;</p>
        </div>
      </div>
    </div>
  </div>
  <div id="spinner" class="spinner">
  </div>    
  <div id="spinnerContainer" class="modal fade">
    <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-body">
        Loading...
      </div>
    </div>
  </div>
  </div>
  </body>
</html>

<%def name="get_icon(action)">
  <%
  icon = action.icon.strip()
  if icon == "icon-list-alt":
    icon = "glyphicon glyphicon-list-alt"
  elif icon == "icon-plus":
    icon = "glyphicon glyphicon-plus"
  elif icon == "icon-eye-open":
    icon = "glyphicon glyphicon-eye-open"
  elif icon == "icon-edit":
    icon = "glyphicon glyphicon-edit"
  elif icon in ["icon-eye-delete", "icon-trash"]:
    icon = "glyphicon glyphicon-trash"
  elif icon == "icon-download":
    icon = "glyphicon glyphicon-download"
  elif icon == "icon-export":
    icon = "glyphicon glyphicon-export"
  elif icon == "icon-import":
    icon = "glyphicon glyphicon-import"
  return icon
  %>
</%def>

<%def name="render_item_base_actions(item)">
  <% context_actions = [] %>
  % for action in h.get_item_actions(request, item):
    % if (request.url.find(action.name.lower()) < 0) and s.has_permission((action.permission or action.name.lower()), request.context.item, request):
      <%
      if action.name == "Create":
        title = _('Create new item')
      elif action.name == "List":
        title = _('Open overview')
      elif action.name == "Update":
        title = _('Open in "Edit" mode')
      elif action.name == "Read":
        title = _('Open in "Read" mode')
      elif action.name == "Delete":
        title = _('Delete item')
      else:
        title = _(action.description)
      icon = get_icon(action)
      if not action.is_visible("context"):
        continue
      elif action.name.lower() in ['import', 'export'] or "secondary" in action.display.split(","):
        context_actions.append((action, icon))
        continue
      %>
      <a href="${h.get_action_url(request, item, action.name.lower())}"
        class="btn btn-default" title="${title}"><i class="${icon}"></i></a>
    % endif
  % endfor
  <div class="btn-group">
    <button type="button" class="btn btn-default dropdown-toggle"
    data-toggle="dropdown"> ${_('Advanced')} <span class="caret"></span></button>
    <ul id="context-menu-options" class="dropdown-menu  pull-right" role="menu">
      <li role="presentation" class="dropdown-header">${_('Administration')}</li>
      <li><a href="${h.get_action_url(request, item, 'ownership')}">${_('Change ownership')}</a></li>
      % if len(context_actions) > 0:
        <li class="divider"></li>
        <li role="presentation" class="dropdown-header">${_('Advanced actions')}</li>
        % for action, icon in context_actions:
          <li>
            <a href="${h.get_action_url(request, item,
            action.name.lower())}"><i class="${icon}">&nbsp;</i>${_(action.name)}</a>
          </li>
        % endfor
      % endif
    </ul>
  </div>
</%def>

## flash messages with css class und fade in options
<%def name="flash_messages()">
  % for message in request.session.pop_flash('success'):
    <div class="alert alert-success fade in out">
      ${message}
    </div>
  % endfor
  % for message in request.session.pop_flash('info'):
    <div class="alert alert-info">
      ${message}
    </div>
  % endfor
  % for message in request.session.pop_flash('error'):
    <div class="alert alert-danger fade in out">
      ${message}
    </div>
  % endfor
</%def>
