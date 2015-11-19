<% 
last_login = s.get_last_successfull_login(request, request.user)
last_failed_login = s.get_last_failed_login(request, request.user)
if last_login:
  failed_logins = s.get_last_logins(request, last_login.datetime, success=False)
else:
  failed_logins = []
login_fishy = len(failed_logins) > 5
%>
% if request.user and request.registry.settings.get("layout.show_logininfo") == "true" and last_login:
% if login_fishy:
<div class="row">
  <div class="col-md-12">
    <div id="logininfowarning" class="alert alert-warning" role="alert">
      ##<p><strong>${_('Login Warning!')}</strong></p>
      <p>
        <i style="font-size: x-large; vertical-align: bottom" class="fa
          fa-lock">&nbsp;</i>
        ${_("There have been more than <strong>5 failed login attemps</strong> since the last successfull login on <strong>%s</strong>") % h.prettify(request, last_login.datetime) | n}.
        ${_("This could be an <strong>attempt of misuse</strong> of your user account.") | n}
      </p>
    </div>
  </div>
</div>
% endif
<div class="row">
  <div class="col-md-12">
    <span id="logininfo" class="text-muted pull-right">
      ${_('The last login was on %s') % (h.prettify(request,
      last_login.datetime))}<br>
      % if last_failed_login:
      ${_('The last failed login was on %s') % (h.prettify(request, last_failed_login.datetime))}
      % endif
    </span>
  </div>
</div>
%endif
