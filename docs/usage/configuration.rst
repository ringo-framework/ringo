*************
Configuration
*************
The application can be configured by setting values in the
``ini`` file. Ringo provides some helper methods to give directly access to
some of the configuration options.

Application
===========
Helper methods giving access to the configuration options are available in the `appinfo` module.

.. automodule:: ringo.lib.helpers.appinfo
   :members: get_app_mode, get_app_title, get_app_logo, get_app_inheritance_path

.. index::
   single: Configuration; Title

Title
-----
The name of the application used at various places in the application
can be configured with the following varible.

* app.title = Application name 

The title is available using the :func:`get_app_title` function.

.. index::
   single: Configuration; Custom static files
   see: Branding; Configuration

Custom static directory
-----------------------
It is possible to define a directory to include custom static files which
should not be part of the application. This can be usefull for application
branding to place custom logo graphics etc. You can define the path to the
root of that custom static folder.

* app.customstatic = /path/to/your/folder

If not defined it will be ringo:static.

.. index::
   single: Configuration; Logo

Logo
----
The logo of the application used in the header of the page. You can define a
path to the logo relative to the given custom static directory which should be
displayed. If no logo is set then no logo is displayed at all.

If you need more customization on the logo, then you need to overwrite the
logo.mako template.

* app.logo = images/ringo-logo-64.png

The logo is available using the :func:`get_app_logo` function.

.. index::
   double: Configuration; Inheritance
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

The inheritance_path is available using the :func:`get_app_inheritance_path`
function.

Example:
The current application package is named "foo". "foo" is based on "bar". And
"bar" is based on "ringo". The inheritance path is foo->bar->ringo.

This has consequences for the loading of form and table configurations.
When trying to load form or table configuration ringo will iterate over
the inheritance path and try to load the configuration from each
application within the inheritance path.

Application Locale
------------------
The locale is used to format dates times in the application.  On default Ringo
determines the locale by looking into the request getting the browser language
setting. However you can enforce setting the locale of the application by
setting the following config variable in your config

* app.locale =

If added (In the mean of adding the variable at all) the locale will be
enforced. An empty value means use a "default" encoding which leads to dates
formatted in ISO8601. Otherwise the locale must match a known ISO-3166 locale
string.

Application Mode
----------------
The application can be configured to be in a special "mode". Where mode can be
a demo, development, education or any other flavour of your application.
Setting the mode will result in some visual indication which is is different
to the normal application mode.

* app.mode =

Short description of the mode. If this value is set a application will have
some visual indication.

* app.mode_desc =

A longer description of the mode.

* app.mode_color_primary = #F2DEDE
* app.mode_color_secondary = red

The color of the mode indicator header and the border around the application.
Defaults to #F2DEDE (light red) and red. Allowed values are any usable in CSS,
such as hexadecimal or RGB values, named colors, etc.

The mode is available using the :func:`get_app_mode` function.

.. index:: Testing mode

Testmode
""""""""
You can set the application in some test mode which is usefull to test the
application. To enable the testmode set the `app.mode` attribute to *testing*.

In this mode you can start Testcases which are embedded in its own transaction
on the database.
In a Testcase you can do a series of queries to the application and add, delete or
modify data. 
When you stop the Testcase the changes you have made in the Testcase will be
rolled back.

When enabled the webinterface has an additional link to start and end a
Testcase which will be handled in a transaction.

In unittests you can use the following URLs to start a Testcase:

* /_test_case/start
* /_test_case/stop


History ignores
---------------
You can configure URL which will be ignored in history. This is often needed
in case you do AJAX requests to fetch data. As you do not want those URL be
part of the history you can configure to ignore those URLs.

* app.history.ignore = /foo,/bar,/baz

The ignore list is a comma separated list of fragments of an URL. The code
will check if the current URL starts with one of the defined ignores.

Cache
-----
You can configure to cache the loaded configurations for the form
configs. This is usefull in production mode for a significant speed up
when loading large forms with many rules and conditionals.

* app.cache.formconfig = true

The default is not to cache the configuration.

Feature Toggles
---------------
Feature toggles can be used to enable specific code paths in the
application by setting a config variable in the ini file. This is
usefull to make features which are currently under development available

Feature toggles are set in the *ini* file like this:: 

    feature.mynewfeaure = true.

The configuration is available in the current request and can be used
everywhere in the application where the request is available.::

    if request.ringo.feature.mynewfeaure:
        # Feature is anabled
        pass
    else:
        # Feature is not anabled
        pass

Please note that the value in the configuration must be set to *true* to
consider the feature to be enabled. If the feature is set to anything
different or isn't configured at all it is considered to be not enabled.

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

.. _admin_autologout:

Autologout
----------
The authentication only stay valid for the given time. After that time a
automatic logout from the application will happen.


auth.timeout
        Defaults to 1800 seconds.

auth.timeout_warning
        Defaults to 30 seconds.

The timeout_warning variable defines how many seconds before the actual logout a
warning dialog will be raised.

If you want to display a nice sessiontimer than look also in :ref:`admin_sessiontimer`.

Passwort reminder and user registration
---------------------------------------
Ringo provides methods to allow users to register a new account or send
requests to reset their passwords. Botch subsystems can be enabled by changing
the following values.

auth.register_user
        Defaults to `false`. Enable the option to let users register a new
        account. However the account must be *finished* by the administrator.

auth.register_user_default_roles
        Defaults to the default user role. Can be defined as a comma separated
        list of role ids.

auth.register_user_default_groups
        Defaults to the default user group. Can be defined as a comma separated
        list of group ids.

auth.password_reminder
        Defaults to `false`. Enable the option to let the user reset their
        password.

.. note::
    To enable this feature the mailsystem must be configured too. You
    need to set the mail host and the default sender in your config.

.. note::
    To enable this feature the mailsystem must be configured too. You
    need to set the mail host and the default sender in your config.

Authentification callback
-------------------------
You can configure a callback method which is called after the user is
basically authenticated. This callback can be used to cancel the
authentification proccess by doing further checks on the user, or
trigger some actions after the user logs in. The callback must have the
following form::

        from ringo.lib.security import AuthentificationException

        def auth_callback(request, user):
            # permit admin user to login.
            if user.login == "admin":
                raise AuthentificationException("Admin is not allowed")

To cancel the authentification the function must raise an exception. The message
of the exception is used as error message. In all other cases to user is
authenticated.

Can need to configure this callback in the *ini* file:

auth.callback = foo.bar.callback

*foo.bar.callback* must be the modul path which can be used to import the
function.

.. _anonymous_access:

"Anonymous" access
------------------
But you can define a default user which is used as authenticated user:

auth.anonymous_user
        Defaults to None. So no user is authenticated.

.. warning::
    If enabled every user which enters the application will use the
    application as the configured user in the same way as the user really logs
    in.

You can define the user by givin the loginname of the user. Of course
the user must be present in the application.


Layout
======


Default Overview complexity
---------------------------

.. versionchanged:: 1.5
   Prior version 1.5 the default overview was always the more complex
   overview.

You can define which complexity the the overview pages in
ringo will have on default. There are two complexities available:

1. A simple Overview. This overview provides a simple
   search widget which may be enough for the most use cases.
2. A advanced more complex overview. This overview provides a stackable
   search, regular expressions, pagination and a feature to save a search.

* layout.advanced_overviews = Default is false, which means without
  further configuration the simple overviews are used.

The complexity can be configured per overview table using the
``table.json`` configuration which is available for all tables in the
system.

.. _admin_sessiontimer:

Session Timer
-------------
You can configure to show a session timer widget in the header of the
application. The session timer will show the time left in the current session
and provides a button to refresh the session.

* layout.show_sessiontimer = true.
  
Default is false, no widget is shown.

The time of the session timer is configured in :ref:`admin_autologout`.

Login Info
----------
You can configure to show the last successful and last failed login on the
start page. This can help the user to identify possible misuse of their
account.

Additionally a warning is shown if there has been more than 5 failed login
attemps since the last successful login.

* layout.show_logininfo = true.

Default is false, no info is shown.

.. note::
        The login info is an inclued mako file in the index.mako template.
        Please do not forget to include the logininfo.mako template in your
        index page in case you have overwritten the index page.



Read and Update Pages
=====================

.. index::
   single: String Representation

Modulname in title
------------------
Usually the title of the entry is in the format "Name of the modul: String
representation of the modul".

You configure to omit the leading name of the modul to have more space and
options to show a more custom title your own title.

* layout.show_modulname = true

Default is true, so the name of the modul is shown is shown.

Contextmenu
-----------
You can configure if the context menu will be displayed in the detailed item
view. For simple applications this menu might provide too much functionallity
which tends to be confusing to other users. So you can completeley disable it.

.. image:: images/screenshots/ui/contextmenu.png

* layout.show_contextmenu = true

Default is true, so the menu is shown.

.. note::
   
   This setting only applies for users who does not have the admin role!
   Admins will always see the contextmenu available. Please not if your
   disable the menu the users will loose access to some default actions like
   changing the ownership. 

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

DB Caching
==========
.. warning::
        This feature is experimantal. It might change or removed completely in
        the next versions of Ringo.

Ringo supports file based caching of DB queries using a dogpile cache. Caching
is disabled on default and must be enabled.

.. note::
        Ringo does not try to use the cache on default. You will need to
        write code to tell Ringo to do so explicit! Unless you do not have any
        code that tries to use the cache you will not need to enable it here
        at all.

To enable the cache you need to define where to save the cache:

 * db.cachedir = path/to/the/cachebasedir

The queries are cached in so called `regions` which will stay valid for a
given time before the cache is invalidated. The regions can be configured in
the following way:

 * db.cacheregions = default:3600 short:50 ...

The multiple regions are separated with spaces. A singe regions consists of the
name and the time the regions should be valid. Name and time is colomn
separated.


Mail
====
The configuration of the Mail system is described in detail in the
`documentation of the pyramid_mailer library
<http://docs.pylonsproject.org/projects/pyramid_mailer/en/latest/#configuration>`_

Below you find a show overview of the most common used settings. If you need
more of the settings it is save to add them to your configuration.


 * mail.host =

This is the host where your MTA will listen on port 25 to receive the mails
which it will transfer to the recipients.

 * mail.default_sender =

This is the default sender email (From:) of the mails sent from this
application. Often this will be changed within the application anyway but we
need to be sure we have a default sender. Often this is a "noreply@foo.bar"
address.

 * mail.username =
 * mail.password =

In case your MTA requires some sort of authentication you can set it here.

Converter
---------
The converter has become part of the `ringo printtemplates
extension <https://github.com/ringo-framework/ringo_printtemplates>`_. It is
used to convert ODS files into PDF files.

Please see the README of the library for more details on how to configure the
converter.


