*************************
Application Configuration
*************************
Application
===========

Title
-----
The name of the application used at various places in the application
can be configured with the following varible.

* app.title = Application name 

Application Url
---------------
Optional. Not defined on default. The application URL can be defined to
set a specific prefix for URL. This currently only used on client side
for AJAX requests. In most cases this does not need to be set.

* app.url: Baseurl of the application. Defaults to not set.

Leave the variable empty to set the base url to tha value of
request.application.url. Otherwise the value of this config variable is
used.

.. _config_app_base:

Application Base
----------------
Optional. Usually a ringo based application is directly based on ringo.
So the default inheritance path of your application is foo->ringo (in
case your application package is called "foo").

* app.base = Default is not set

If your application is based on another ringo based application you can
configure the name of the application here. Setting this configuration
will modify the inheritance path of the application.

Example:
The current application package is named "foo". "foo" is based on "bar". And
"bar" is based on "ringo". The inheritinace path is foo->bar->ringo.

This has consequences for the loading of form and table configurations.
When trying to load form or table configuration ringo will iterate over
the inhertance path and try to load the configuration from each
application within the inhertance path.

Sessions
========

Beaker is used for session handling. Please refer to its documentation to get
more information on the available configuraton options.

 * session.type = file
 * session.data_dir = %(here)s/data/sessions/data
 * session.lock_dir = %(here)s/data/sessions/lock
 * session.key = customerskey
 * session.timeout = 1800

The following options regard to the cookie identifying the session in the
client. The configuration option are taken from the global cookie security
settings:

 * session.secret = %(security.cookie_secret)s
 * session.secure = %(security.cookie_secure)s
 * session.cookie_expires = %(security.cookie_expires)s
 * session.httponly = %(security.cookie_httponly)s
 * session.path = %(security.cookie_path)s
 * session.domain = %(security.cookie_domain)s

Authentification
================
Authetification is stored with in a auth_tkt cookie.  See `Cookie options on
<http://docs.pylonsproject.org/projects/pyramid/en/latest/api/authentication.html>`_
for more details.

The following setting as taken from the global cookie security settings:

 * ``cookie_secret`` to sign the cookie data.
 * ``cookie_secure`` to only send the cookie over a save (SSL) connection.
 * ``cookie_ip`` to bind the cookie to a specific IP.
 * ``cookie_httponly`` to disallow clientside access to the cookie
 * ``cookie_path`` to set the scope of the cookie to a specific path.
 * ``cookie_domain`` to set the scope of the cookie to a specific domain.

Autologout
-----------
The authentification only stay valud for the given time. After that time a
automatic logout from the application will happen.

 * auth.timeout = 1800

Passwort reminder and user registration
---------------------------------------
Ringo provides methods to allow users to register a new account or send
requests to reset their passwords. Botch subsystems can be enabled by changing
the following values.

 * auth.register_user = false
 * auth.password_reminder = false

Security
========
CSRF Protection
---------------
To enable CSRF protection you can configure ringo to include a CSRF
synchronizer token to each form to protect POST request against CSRF attacks.

 * security.enable_csrf_check = true

However, for testing issues it might be usefull to disable this feature.

Cookies
-------

 * security.cookie_secret = 'secret'
 * security.cookie_secure = false
 * security.cookie_ip = false
 * security.cookie_httponly = false
 * security.cookie_expires = true
 * security.cookie_path = '/'
 * security.cookie_domain =

The `cookie_ip` setting will only apply to the `auth_tkt` cookie for the
authorisation. Other option apply for all cookies set.

.. _conf_headers:

Headers
-------
See `this page <http://ghaandeeonit.tumblr.com/post/65698553805/securing-your-pyramid-application>`_ for more informations.

 * security.header_secure = true
 * security.header_clickjacking = true
 * security.header_csp = false

You can define `CSP Options <http://en.wikipedia.org/wiki/Content_Security_Policy>`_ by configuring one of the following
options:

 * security.csp.default_src
 * security.csp.script_src
 * security.csp.object_src
 * security.csp.style_src
 * security.csp.img_src
 * security.csp.media_src
 * security.csp.frame_src
 * security.csp.font_src
 * security.csp.connect_src
 * security.csp.sandbox
 * security.csp.frame_ancestors

Caching
-------
Number of seconds the cached content will stay valid. A value of non means no
caching at all and all elements are loaded on every request.

The enhance the security follwing the recommodation of measurement M 4.401 of
`BSI Grundschutz <https://www.bsi.bund.de/DE/Themen/ITGrundschutz/ITGrundschutzKataloge/Inhalt/_content/m/m04/m04401.html;jsessionid=116E42B16FBC9D779FD768E7CDE905A1.2_cid368>`_ you should disable the caching.

 * security.page_http_cache = 0
 * security.static_http_cache = 3600

.. note::
   The caching setting of the page currently only applies to the CRUD
   operations of the modules and not to the static pages like contact, home
   etc.

.. warning::
   Caching of dynmic generated pages might result in some unexpected behaviour
   such as outdated items in overview lists. Therefor ther default disables
   caching here.

Mail
====
 * mail.host =
 * mail.default_sender =
 * mail.username =
 * mail.password =

Converter
=========
.. note::
   To be able to use the converter you need to install the "converter" extra
   requirements. See ``setup.py`` file for more details.

 * converter.start = false
 * converter.pythonpath =
