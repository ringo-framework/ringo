% if field.is_readonly():
  <div class="readonlyfield" name="${field.name}" value="${field.get_value()}">
    ${field.renderer.render_link() or field.get_value(expand=True) or "&nbsp;"}
  </div>
% else:
  <select class="form-control" id="${field.id}" name="${field.name}">
    % for option in options:
      ## Depending if the options has passed the configured filter the
      ## option will be visible or hidden
      % if option[2]:
        <option value="${option[1]}">${option[0]}</option>
      % elif not field.renderer.remove_filtered == "true":
        <option value="${option[1]}" class="hidden">${option[0]}</option>
      % endif
    % endfor
  </select>
% endif
