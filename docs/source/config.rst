#############
Configuration
#############

Authentification
================
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
See `Cookie options on <http://docs.pylonsproject.org/projects/pyramid/en/latest/api/authentication.html>`_ for more details.

 * security.cookie_secret = 'secret'
 * security.cookie_secure = false
 * security.cookie_ip = false
 * security.cookie_path = '/'
 * security.cookie_httponly = false

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
