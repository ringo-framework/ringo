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
"bar" is based on "ringo". The inheritance path is foo->bar->ringo.

This has consequences for the loading of form and table configurations.
When trying to load form or table configuration ringo will iterate over
the inheritance path and try to load the configuration from each
application within the inheritance path.

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
client. The configuration option are taken from the global :ref:`conf_cookies`
security settings:

session.secret 
        Defaults to *security.cookie_secret*

session.secure
        Defaults to *security.cookie_secure*

session.cookie_expires
        Defaults to *security.cookie_expires*

session.httponly
        Defaults to *security.cookie_httponly*

session.path 
        Defaults to *security.cookie_path*

session.domain
        Defaults to *security.cookie_domain*

Authentification
================
Authentication is stored with in a auth_tkt cookie.  See `Cookie options on
<http://docs.pylonsproject.org/projects/pyramid/en/latest/api/authentication.html>`_
for more details. The settings as taken from the global :ref:`conf_cookies`
security settings.

Autologout
-----------
The authentication only stay valid for the given time. After that time a
automatic logout from the application will happen.

3 Minutes before the logout actually happens the application will raise a
warning dialog.

..note::
        Because of the warning 3 minutes before the logout happens it does not
        make much sense to set the value lower than 200 seconds. Otherwise
        the warning will show up almost immeditately after the login.

auth.timeout
        Defaults to 1800 seconds.

Passwort reminder and user registration
---------------------------------------
Ringo provides methods to allow users to register a new account or send
requests to reset their passwords. Botch subsystems can be enabled by changing
the following values.

auth.register_user
        Defaults to `false`. Enable the option to let users register a new
        account. However the account must be *finished* by the administrator.

auth.password_reminder
        Defaults to `false`. Enable the option to let the user reset their
        password.

Security
========
CSRF Protection
---------------
To enable CSRF protection you can configure ringo to include a CSRF
synchronizer token to each form to protect POST request against CSRF attacks.

security.enable_csrf_check = true
        Defaults to `true`

However, for testing issues it might be useful to disable this feature.

.. _conf_cookies:

Cookies
-------
security.cookie_secret
        Defaults to a randomly generated 50 char long string. Value used to
        sign the cookie to prevent manipulation of the content of the cookie.
        If not set the value will be regenerated on every application start.

        .. tip::
           During development it is usefull to set the value to a static
           string to prevent invalidating the cookie on every application
           restart.

        .. important::
           In productive operation: Please ensure that this value is set to a randomly generated
           string. Either by not setting the value at all (and let the application generate a random string) or setting it to a static random generated string.

security.cookie_secure
        Default to `false`. If set to `true` the cookie is only accessible
        over a secure connection (SSL).

        .. important::
           In productive operation: Please ensure that this value is set to
           true if you use a SSL enabled connection.

security.cookie_ip
        Defaults to `true`. If set to `true` the cookie is bound to the IP
        address.

        .. caution::
           Although this settings **can** increase the security it may cause
           problems in if the IP address is not stable which is true for most
           dialup connections.

security.cookie_httponly
        Defaults to `true`. If set to `true` the cookie is not accessible
        directly by the client but can only be changed through a http
        connection.

security.cookie_expires
        Defaults to `true`. If set to `true` the cookie will expires after the
        browser is closed.

security.cookie_path
        Defaults to `/`. The scope of the cookie will bound to the given path
        in the application.

security.cookie_domain
        Defaults to the current domain and all subdomains (is automatically determined by the
        server). The scope of the cookie will bound to a specific domain.

security.cookie_name
        Defaults to 'auth_tkt'. Needs to be set in case you have multiple
        ringo applications on the same server.

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
