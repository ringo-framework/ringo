## The form tag will overwrite the rendererd form tag coming from the
## formbar rendering. At least in FF
% if not items:
<form action="${ok_url}" method="POST" enctype="multipart/form-data">
  <div class="dialog modal fade" id="myModal">
    <div class="modal-dialog">
      <div class="panel panel-default">
        <div class="panel-heading"><strong>${_('Import configuration for')} ${modul}</strong></div>
          <div class="panel-body">
            <p>${body}</p>
          </div>
          <div class="panel-footer">
            <button type"submit" class="btn btn-primary">${action}</button>
            <a class="btn btn-default" href="${cancel_url}">${_('Cancel')}</a>
            <input type="hidden" name="confirmed" value="1"/>
            <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}"/>
          </div>
        </div>
      </div>
    </div>
  </div>
</form>
% else:
  <div class="dialog modal fade" id="myModal">
    <div class="modal-dialog">
      <div class="panel panel-info">
        <div class="panel-heading"><strong>${_('Import results')} ${modul}</strong></div>
          <div class="panel-body">
          <table class="table">
            <tr>
              <th>${_('Name')}</th>
              <th width="50">${_('Type')}</th>
              <th width="50">${_('Result')}</th>
            </tr>
          % for item in items:
            <tr>
              <td><a href="${request.route_path(item[0].get_action_routename('read'), id=item[0].id)}">${item[0]}</a></td>
              <td>${item[1]}</td>
              <td>
                % if item[2]:
                  ${_('Ok')}
                % else:
                  ${_('Failure')}
                % endif
            </tr>
          % endfor
          </table>
          </div>
          <div class="panel-footer">
            <a class="btn btn-default" href="${overview_url}">${_('Overview')}</a>
          </div>
        </div>
      </div>
    </div>
% endif
