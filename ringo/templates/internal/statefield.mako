<div class="panel panel-info">
  <div class="panel-heading">
    <label for="${field.id}">${field.label}</strong>
  </div>
  <div class="panel-body">
    <p>
      <strong>Current state:</strong> ${state._label}</br>
      <small>${state._description}</small>
    </p>
    % if not field.is_readonly():
    <p>
      <strong>State transition:</strong></br>
      <select id="${field.id}" name="${field.name}" class="form-control">
        <option value="${state._id}">No Transition</option>
        % for trans in transitions:
            <option value="${trans._end_state._id}">${trans._label}</option>
        % endfor
      </select>
      <small><strong>Resulting State:</strong></br>
      Description of resulting State</small>
    </p>
    % endif
  </div>
</div>
