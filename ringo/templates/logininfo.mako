<% 
last_login = s.get_last_successfull_login(request, request.user)
login_fishy = len(s.get_last_logins(request, last_login.datetime, success=False)) > 5
%>
% if not login_fishy:
  <span id="logininfo" class="bg-info pull-right">
    <small>
    ${_('The last login was on %s') % (h.prettify(request, last_login.datetime))}
    </small>
  </span>
% else:
  <div id="logininfowarning" class="alert alert-warning" role="alert">
    <p><strong>${_('Attention!')}</strong></p>
    <p>
      ${_("There has been more than <strong>5 failed login attemps</strong> since the last successfull login on %s" % h.prettify(request, last_login.datetime)) | n}<br>
      ${_("This could be an indication of an <strong>attempt of misuse</strong> of your user account. If the failed logons can not be explained, please <strong>contact your administration</strong>.") | n}
    </p>
  </div>
% endif
