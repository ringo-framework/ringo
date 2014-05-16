<div class="panel panel-info">
  <div class="panel-heading">
    <label for="${field.id}">${field.label}</label>
  </div>
  <div class="panel-body">
    % if not field.is_readonly():
    <p>
      <strong>State transition:</strong><br/>
      <select id="${field.id}" name="${field.name}" class="form-control">
        <option value="${state._id}">No Transition</option>
        % for trans in state.get_transitions():
            <option value="${trans._end_state._id}">${trans._label}</option>
        % endfor
      </select>
    </p>
    % endif
    <div class="row">
      <div class="col-sm-6">
        <p>
          <strong>Current state:</strong> ${state._label}<br/>
          <small>${state._description}</small>
        </p>
      </div>
      <div class="col-sm-6">
        % for trans in state.get_transitions():
          <div class="result-state" id="result-state-${trans._end_state._id}">
            <strong>Resulting State:</strong>
            ${trans._end_state._label}<br/>
            <small>
            ${trans._end_state._description}
            </small>
          </div>
        % endfor
      </div>
    </div>
  </div>
</div>

<script>
  $("#${field.id}").change(function() {
    var selected = $(this).val();
    $(".result-state").each(function(selected) {
      $(this).hide();
    });
    $("#result-state-"+selected).show();
  });
</script>
