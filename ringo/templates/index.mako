<%inherit file="/main.mako" />
<%
mapping={'app_title': h.get_app_title()}
%>
<div class="page-header">
<h1>Home</h1>
</div>
<h2>${_('Welcome to ${app_title}!', mapping=mapping)}</h2>
<p>${_('What you see here is the default dashboard and layout based on the Ringo application framework. This is your home. Your dashboard. Usually this page is used to give and overview on the most important things like appointments, news and more in this application.')}</p>
% if not request.user:
<h2>${_('Next stop: Login!')}</h2>
<p>${_('This is the dashboard as seen by anonymous users. To get a better impression of the functionality provided by Ringo then you can login now.<br></br>Please login withe the following credentials:') | n}</p>
<ul>
  <li>${_('Loginname')}: admin</li>
  <li>${_('Password')}: secret</li>
</ul>
<p>${_('Please do not forget to change the password after your first login! What are you waiting for?')}</p>
<a href="${request.route_path('login')}" class="btn btn-primary btn-large" title="${_('Login in the application')}">${_('Login')}</a>
% else:
<h2>${_('What to do next?')}</h2>
<p>${_('The Ringo application framework provides already some basic functionality which is ready for use in your fresh created application. It time to make a tour in your application to get a better impression of what is already included and how things work.') | n}</p>
<p>${_('You probably want to change this page and other things. No problem. A good starting point is the documentation. Please consult the part on development and learn how to change and add things to this application. Happy coding! :)')}</p>
<h2>${_('News')}</h2>
${news | n}
<h2>${_('Reminders')}</h2>
${reminders | n}
% endif
