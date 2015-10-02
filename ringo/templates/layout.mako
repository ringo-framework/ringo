<%
mode = h.get_app_mode(request) 
%>
<%inherit file="/base.mako" />
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
