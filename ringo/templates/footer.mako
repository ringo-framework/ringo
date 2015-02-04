<div class="container">
  <div class="row">
    <div class="col-sm-6">
      % if len(h.get_modules(request, 'admin-menu')) > 0:
        <ul class="list-unstyled">
          <li class="dropdown dropup">
            <a href="#" data-toggle="dropdown"><img src="${request.static_path('ringo:static/images/icons/16x16/applications-system.png')}"/>${_('Administration')}<b class="caret"></b></a>
            <ul class="dropdown-menu dropup-menu" role="menu">
              % for modul in h.get_modules(request, 'admin-menu'):
                <li><a href="${request.route_path(modul.name+'-list')}">${_(modul.get_label(plural=True))}</a></li>
              % endfor
            </ul>
          </li>
        </ul>
      % endif
    </div>
    <div class="col-sd-6">
      <ul class="list-inline pull-right">
        <li>
          <a href="${request.route_path('about')}">${_('About')}</a>
        </li>
        <li>
          <a href="${request.route_path('contact')}">${_('Contact')}</a>
        </li>
        <li>
          <a href="${request.static_path('%s:static/doc/html/index.html' % h.get_app_name())}" target="_blank">${_('Documentation')}</a>
        </li>
        <li>
          <a href="${request.route_path('version')}" title="${_('Show version information')}">${h.get_app_title()} ver. ${h.get_app_version()}</a>
        </li>
      </ul>
    </div>
  </div>
</div>
