<div id="statefield">
% if field.renderer.layout == "button":
  <label for="${field.id}">${_(field.label)}</label>
  <div class="readonlyfield" name="${field.name}">
      ${_(state._label)}
      ## The value is changed by JS in case the user clicks on the
      ## button to change the state.
      <input type="hidden" name="${field.name}" id="${field.id}" value="${field.get_value()}" datatype="integer"/>
  </div>
  % if state.get_description(request.user):
    <p><small><strong>${_('Description')}:</strong>
        ${state.get_description(request.user) | n}</small></p>
  % endif
  % if len(state.get_transitions()) > 0:
    <p>${_("Please select one of the following steps:")}</p>
    % for num, trans in enumerate(state.get_transitions()):
      <button class="btn btn-default btn-block" type="submit" id="btn_state_${num}_${field.name}">${_(trans._label)}</button>
      <script>
        $('#btn_state_${num}_${field.name}').click(function() {
          $('input[name="${field.name}"]').val(${trans._end_state._id})
        })
      </script>
    % endfor
  % endif
% elif field.renderer.layout == "simple":
<label for="${field.id}">${_('State')}</label>
<select id="${field.id}" name="${field.name}" class="form-control">
  <option value="${state._id}" selected="selected">${_(state._label)}</option>
  % for trans in state.get_transitions():
      <option value="${trans._end_state._id}">${_(trans._label)}</option>
  % endfor
</select>
% else:
<div class="panel panel-info">
  <div class="panel-heading">
    <label for="${field.id}">${_(field.label)}</label>
  </div>
  <div class="panel-body">
    % if not field.readonly:
    <p>
      <strong>${_('State transition')}:</strong><br/>
      <select id="${field.id}" name="${field.name}" class="form-control">
        <option value="${state._id}" selected="selected">${_('No Transition')}</option>
        % for trans in state.get_transitions():
            <option value="${trans._end_state._id}">${_(trans._label)}</option>
        % endfor
      </select>
    </p>
    % endif
    <div class="row">
      <div class="col-sm-6">
        <p>
          <strong>${_('Current state')}:</strong> ${_(state._label)}<br/>
          <small>${_(state.get_description(request.user))}</small>
        </p>
      </div>
      <div class="col-sm-6">
        % for trans in state.get_transitions():
          <div class="result-state" id="result-state-${trans._end_state._id}">
            <strong>${_('Resulting State')}:</strong>
            ${_(trans._end_state._label)}<br/>
            <small>
              ${_(trans._end_state.get_description(request.user))}
            </small>
          </div>
        % endfor
      </div>
    </div>
  </div>
</div>
% endif
</div>
<div id="statefieldinfo" class="alert alert-info" role="info">
  ${_('Form must not have unsaved changes. Please save outstanding changes before changing the state.')}
</div>

<script>
  $(function() {
    $("#${field.id}").change(function() {
      var selected = $(this).val();
      $(".result-state").each(function(selected) {
        $(this).hide();
      });
      $("#result-state-"+selected).show();
    });
    $("div.formbar-form").on("clean", function() {
        $('#statefieldinfo').hide();
        $('#statefield button, #statefield select').each(function() {
          $(this).prop('disabled', false);
        })
    });
    $("div.formbar-form").on("dirty", function() {
        $('#statefieldinfo').show();
        $('#statefield button, #statefield select').each(function() {
          $(this).prop('disabled', true);
        })
    });
  });

</script>
