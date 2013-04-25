<table id="data" class="table table-striped table-hover table-condensed">
  <tr>
  % for field in headers:
    <th>
      % if request.session['%s.list.sort_order' % clazz.__tablename__] == "asc":
        <a href="${request.current_route_url()}?sort_field=${field[0]}&sort_order=desc">${field[1]}</a>
      % else:
        <a href="${request.current_route_url()}?sort_field=${field[0]}&sort_order=asc">${field[1]}</a>
      % endif
      % if request.session['%s.list.sort_field' % clazz.__tablename__] == field[0]:
        % if request.session['%s.list.sort_order' % clazz.__tablename__] == "asc":
          <i class="pull-right icon-arrow-up"></i>
        % else:
          <i class="pull-right icon-arrow-down"></i>
        % endif
      % endif
    </th>
  % endfor
    <th>
      Actions
    </th>
  </tr>
  % for item in items:
  <tr>
    % for field in headers:
    <td>
        <% value = getattr(item, field[0]) %>
        ## Escape value here
        % if isinstance(value, list):
          ${", ".join(unicode(v) for v in value) | h}
        % else:
          ${value | h}
        % endif
    </td>
    % endfor
    ## Actions
    <td>
      <a href="read/${item.id}">Read</a>
    </td>
  </tr>
  % endfor
  % if len(items) == 0:
  <tr>
    <td colspan="${len(headers)}">
    No items found
    </td>
  </tr>
  % endif
</table>
