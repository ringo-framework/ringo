<div class="dialog modal hide fade" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
<div class="modal-header">
<h3 id="myModalLabel"><img src="${icon}"> ${header}</h3>
</div>
<div class="modal-body">
<p>${body}</p>
</div>
<div class="modal-footer">
<form action="${ok_url}" method="POST">
  <a class="btn" href="${cancel_url}">${_('Cancel')}</a>
  <input type="hidden" name="confirmed" value="1"/>
  <button type"submit" class="btn btn-primary">${action}</button>
</form>
</div>
</div>
