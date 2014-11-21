% if field.is_readonly():
  <div class="readonlyfield" name="${field.name}" value="${field.get_value()}">
    % if field.get_previous_value() is not None:
      ${renderer._render_diff(_(field.get_previous_value("", expand=True)),
        field.renderer.render_link() or _(field.get_value(expand=True)) or "&nbsp;")}
    % else:
      ${field.renderer.render_link() or _(field.get_value(expand=True)) or "&nbsp;"}
    % endif
  </div>
% else:
  <select class="form-control" id="${field.id}" name="${field.name}">
    % for option in options:
      ## Depending if the options has passed the configured filter the
      ## option will be visible or hidden
      % if option[2]:
        % if unicode(option[1]) == unicode(field.get_value()):
          <option value="${option[1]}" selected="selected">${_(option[0])} </option>
        % else:
          <option value="${option[1]}">${_(option[0])}</option>
        % endif
      % else:
        % if unicode(option[1]) == unicode(field.get_value()):
          <option value="${option[1]}" selected="selected">${_(option[0])}</option>
        % endif
      % endif
    % endfor
  </select>
% endif
