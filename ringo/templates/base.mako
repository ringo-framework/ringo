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
    <link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet" media="screen">
    <link href="/css/layout.css" rel="stylesheet" media="screen">
    <link href="/css/widgets.css" rel="stylesheet" media="screen">
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
  ${next.body()}
    <!-- Move JS to the bottom of the page -->
    <script src="/static/js/jquery.js"></script>
    <script src="/static/bootstrap/js/bootstrap.min.js"></script>
    <script src="/static/js/dataTables.js"></script>
    <script src="/static/js/init.js"></script>
    <script>
      ${h.get_formbar_js() | n}
    </script>
  </body>
</html>

<%def name="render_item_base_actions(item)">
  % for action in item.get_item_modul().actions:
    % if s.has_permission(action.name.lower(), request.context, request):
      <a href="${h.get_action_url(request, item, action.name.lower())}" class="btn"><i class="${action.icon}"></i></a>
    % endif
  % endfor
</%def>

<%def name="render_item_specific_actions(item)">
  ##<a href="${h.get_action_url(request, item, 'list')}" class="btn"><i class="icon-list-alt"></i></a>
  ##<a href="${h.get_action_url(request, item, 'update')}" class="btn"><i class="icon-edit"></i></a>
  ##<a href="${h.get_action_url(request, item, 'delete')}" class="btn"><i class="icon-trash"></i></a>
</%def>
