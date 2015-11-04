<%def name="render_breadcrumb(request)">
  <% breadcrumbs = h.get_breadcrumbs(request) %>
    <div id="breadcrumb" class="container">
      % if breadcrumbs and request.user:
      <ol class="breadcrumb">
      % for element in breadcrumbs:
        % if not(element[1]):
          <li class="active">${element[0]}</li>
        % else:
          <li><a href="${element[1]}">${element[0]}</a></li>
        % endif
      % endfor
      </ol>
    % endif
    </div>
</%def>

${render_breadcrumb(request)}
