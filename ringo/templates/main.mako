<%inherit file="/layout.mako" />
<div class="container">
  <div id="status-messages">
    ${self.flash_messages()}
  </div>
  ${next.body()}
</div>

## flash messages with css class und fade in options
<%def name="flash_messages()">
  % for message in request.session.pop_flash('success'):
    <div class="alert alert-success fade in">
      <button type="button" class="close" data-dismiss="alert">&times;</button>
      ${message}
    </div>
  % endfor
  % for message in request.session.pop_flash('error'):
    <div class="alert alert-danger fade in">
      <button type="button" class="close" data-dismiss="alert">&times;</button>
      ${message}
    </div>
  % endfor
</%def>
