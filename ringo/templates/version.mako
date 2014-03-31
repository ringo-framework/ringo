<%inherit file="/main.mako" />
<div class="page-header">
<h1>Version</h1>
</div>
<p>${_('This page lists the version of some of the most important libraries used by the application.')}</p>
% if app_name != 'ringo':
<h2>${app_title}</h2>
<p>${_('This application.')}</p>
<p>${_('Version')}: ${app_version}</p>
% endif
<h2><img src="${request.static_path('ringo:static/images/ringo-logo-64.png')}" alt="Rinfo logo"/>Ringo</h2>
<p>${_('<a href="https://bitbucket.org/ti/ringo" target="_blank">Ringo</a> is a small Python based high level web application framework build with Pyramid . It provides basic functionality which is often used in modern web applications') | n}</p>
<p>${_('Version')}: ${ringo_version}</p>
<h2>Formbar</h2>
<p>${_('<a href="https://bitbucket.org/ti/formbar" target="_blank">Formbar</a> is a Python library to layout, render and validate HTML forms in web applications.') | n}</p>
<p>${_('Version')}: ${formbar_version}</p>
<h2><img src="${request.static_path('ringo:static/images/sqla-logo.gif')}" alt="SQLAlchemy logo"/>SQLAlchemy</h2>
<p>${_('<a href="www.sqlalchemy.org" target="_blank">SQLAlchemy</a> is Python based ORM mapper.') | n}</p>
${_('Version')}: ${sqlalchemy_version}
<h2><img src="${request.static_path('ringo:static/images/pyramid-logo.jpeg')}" alt="Pyramid logo" width="64"/>&nbsp;Pyramid</h2>
<p>${_('<a href="http://www.pylonsproject.org/" target="_blank">Pyramid</a></a> is a Python based web application framework.') | n}</p>
<p>${_('Version')}: ${pyramid_version}</p>
