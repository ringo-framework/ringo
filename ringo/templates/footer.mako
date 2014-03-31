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
          <a href="" data-toggle="modal" data-target="#helpModal">${_('Documentation')}</a>
        </li>
        <li>
          <a href="${request.route_path('version')}" title="${_('Show version information')}">${h.get_app_title()} ver. ${h.get_app_version()}</a>
        </li>
      </ul>
    </div>
  </div>
</div>

<!-- Modal Help Dialog-->
<div class="modal fade" id="helpModal" tabindex="-1" role="dialog" aria-labelledby="Help" aria-hidden="true">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h4 class="modal-title" id="myModalLabel">${_('Ringo Documentation')}</h4>
      </div>
      <div class="modal-body">
        <iframe
        src="${request.static_path('ringo:static/doc/html/index.html')}"
        frameborder="0" width="100%" height="300"></iframe>
      </div>
    </div>
  </div>
</div>
