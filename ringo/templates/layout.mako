<%inherit file="/base.mako" />
<!-- Part 1: Wrap all page content here -->
<div id="wrap">
  <!-- Begin header content -->
  <div id="header">
    <%include file="/header.mako" />
  </div>
  <!-- Begin page content -->
  <div id="main">
    ${next.body()}
  </div>
</div>
<div id="footer">
  <%include file="/footer.mako" />
</div>
