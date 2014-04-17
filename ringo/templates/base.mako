<!DOCTYPE html>
<html lang="en">
  <head>
    <title>${h.get_app_title()}</title>
    <meta charset="utf-8">
    <meta content="width=device-width, initial-scale=1.0" name="viewport">
    <meta content="" name="description">
    <meta content="" name="author">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap -->
    <link href="${request.static_path('ringo:static/bootstrap/css/bootstrap.min.css')}" rel="stylesheet" media="screen">
    <link href="${request.static_path('ringo:static/bootstrap/css/bootstrap-theme.min.css')}" rel="stylesheet" media="screen">
    <link href="${request.static_path('ringo:static/css/layout.css')}" rel="stylesheet" media="screen">
    <link href="${request.static_path('ringo:static/css/widgets.css')}" rel="stylesheet" media="screen">
    <link href="${request.static_path('ringo:static/css/style.css')}" rel="stylesheet" media="screen">
    % for filename in h.formbar_css_filenames: 
      <link href="${request.static_path('ringo:static/formbar/%s' % filename)}" rel="stylesheet" media="screen">
    % endfor

    <!-- HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
      <script src="../assets/js/html5shiv.js"></script>
    <![endif]-->

    <!-- Fav and touch icons -->
    <link href="${request.static_path('ringo:static/images/icons/favicons/apple-touch-icon-128.png')}" sizes="128x128" rel="apple-touch-icon-precomposed">
    <link href="${request.static_path('ringo:static/images/icons/favicons/favicon.png')}" rel="shortcut icon">
    <script src="${request.static_path('ringo:static/js/jquery.js')}"></script>
    <script src="${request.static_path('ringo:static/bootstrap/js/bootstrap.min.js')}"></script>
    <script src="${request.static_path('ringo:static/js/dataTables.js')}"></script>
    <script src="${request.static_path('ringo:static/js/jquery.jcountdown.min.js')}"></script>
    % for filename in h.formbar_js_filenames: 
      <script src="${request.static_path('ringo:static/formbar/%s' % filename)}"></script>
    % endfor
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
  <script src="${request.static_path('ringo:static/js/init.js')}"></script>
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
  elif icon == "icon-trash":
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
  % for action in item.get_item_actions():
    % if (request.url.find(action.name.lower()) < 0) and s.has_permission((action.permission or action.name.lower()), request.context.item, request):
      <%
      icon = get_icon(action)
      if action.name.lower() in ['import', 'export'] or action.display == "secondary":
        context_actions.append((action, icon))
        continue
      %>
      <a href="${h.get_action_url(request, item, action.name.lower())}"
      class="btn btn-default"><i class="${icon}"></i></a>
    % endif
  % endfor
  <div class="btn-group">
    <button type="button" class="btn btn-default dropdown-toggle"
    data-toggle="dropdown"> ${_('Advanced')} <span class="caret"></span></button>
    <ul id="context-menu-options" class="dropdown-menu  pull-right" role="menu">
      <li><a href="#form">${_('Back to')} ${item.get_item_modul().get_label()}: ${item}</a></li>
      % if owner:
        <li class="divider"></li>
        <li role="presentation" class="dropdown-header">${_('Administration')}</li>
        <li><a href="#ownership">Change ownership</a></li>
      % endif
      % if logbook:
        <li><a href="#logbook">${_('Show logbook')}</a></li>
      % endif
      % if len(context_actions) > 0:
        <li class="divider"></li>
        <li role="presentation" class="dropdown-header">${_('Advanced actions')}</li>
        % for action, icon in context_actions:
          <li>
            <a href="${h.get_action_url(request, item,
            action.name.lower())}"><i class="${icon}">&nbsp;</i>${action.name}</a>
          </li>
        % endfor
      % endif
    </ul>
  </div>
</%def>

<%def name="render_item_specific_actions(item)">
  ##<a href="${h.get_action_url(request, item, 'list')}" class="btn"><i class="icon-list-alt"></i></a>
  ##<a href="${h.get_action_url(request, item, 'update')}" class="btn"><i class="icon-edit"></i></a>
  ##<a href="${h.get_action_url(request, item, 'delete')}" class="btn"><i class="icon-trash"></i></a>
</%def>
