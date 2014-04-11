<form action="${ok_url}" method="POST">
  <div class="dialog modal fade" id="myModal">
    <div class="modal-dialog">
      <div class="panel panel-default">
        <div class="panel-heading"><strong>${_('Export configuration for')} ${modul}</strong></div>
          <div class="panel-body">
            <p>${body}</p>
            <p>${_('You have selected %s %s for export:' % (len(items), modul))}</p>
            <ol>
            % for item in items:
                <li>${item}</li>
            % endfor
            </ol>
          </div>
          <div class="panel-footer">
            <button type"submit" class="btn btn-primary">${action}</button>
            <a class="btn btn-default" href="${cancel_url}">${_('Close')}</a>
            <input type="hidden" name="confirmed" value="1"/>
            <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}"/>
          </div>
        </div>
      </div>
    </div>
  </div>
</form>
