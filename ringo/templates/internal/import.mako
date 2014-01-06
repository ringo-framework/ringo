## The form tag will overwrite the rendererd form tag coming from the
## formbar rendering. At least in FF
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
