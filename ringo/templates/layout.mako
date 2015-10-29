<%
mode = h.get_app_mode(request) 
%>
<%inherit file="/base.mako" />
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
<!-- Part 1: Wrap all page content here -->
% if mode:
<div id="wrap" style="border: 2px solid ${mode[3]};">
% else:
<div id="wrap">
% endif
  <!-- Begin header content -->
  <div id="header">
    <%include file="/header.mako" />
  </div>
  <%include file="/breadcrumbs.mako" />
  <!-- Begin page content -->
  <div id="main">
    ${next.body()}
  </div>
</div>
% if mode:
<div id="footer" style="border-left: 2px solid ${mode[3]}; border-right: 2px solid ${mode[3]}; border-bottom: 2px solid ${mode[3]};">
% else:
<div id="footer">
% endif
  <%include file="/footer.mako" />
</div>
