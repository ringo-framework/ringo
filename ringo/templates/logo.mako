## This element is added above the navigation bar and can be used to include
## some custom logo in the application. Please overwrite this in your
## application
<% logo = h.get_app_logo() %> 
% if logo:
<div id="logo" class="container">
  <div class="row">
    <div class="col-xs-12">
      <img src="${request.static_path(logo)}"/>
    </div>
    ##<div class="col-xs-6">
    ##  <ul class="list-inline pull-right">
    ##    <li><a href="#">FOO</a></li>
    ##    <li><a href="#">BAR</a></li>
    ##  </ul>
    ##</div>
  </div>
</div>
% endif
