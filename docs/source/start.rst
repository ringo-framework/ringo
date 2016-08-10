############
Installation
############

Ringo depends on some external libraries, like `Pyramid
<https://pylonsproject>`_, `SQLAlchemy <https://sqlalchemy.org>`_ and `Formbar <https://formbar.readthedocs.org>`_. Pyramid is a very general open source
Python web framework. SQLAlchemy is a very mature and powerfull ORM to get an
abstraction layer to your database. Formbar is a library to layout and handle
HTML forms in a easy way.

There are of course many ways to get this and other depended libraries
installed on your system. The most easy way is to install all this stuff into
an isolated :ref:`venv`.

**Prerequisites**

 * You will need a Python 2.7.* to get started.
 * PostgreSQL
 * Access to the internet to load depended packages.

The installation of Ringo is done in four steps. First we need to install
some :ref:`basicsupplement` which are needed later in the installation
process.
Second install a :ref:`venv` where all the python packages will be installed.
Third we need a DBMS and therefor install :ref:`installpostgresql`. Finally the last
step will :ref:`bootstrapenv`.

The following examples are tested on a Ubuntu 16.04 installation. 

.. _basicsupplement:

*************************
Basic supplement packages
*************************
*Curl* is used to fetch the bootstrap script which is used in the last step of
the installation.

*Git* is the SCM tool of choice for the Ringo development. To be able to
checkout the related packages during the bootstrap process you need to install
git.

Install all supplement packages::

        apt-get install curl git

.. _venv:

**********
Virtualenv
**********
A `virtualenv <https://pypi.python.org/pypi/virtualenv>`_ is a isolated python
environment is used to install python packages independently from
your systems python environment. Using virtualenv you can setup unlimited number
of independent environments for your development.

Install the virtualenv using the package manger::

        apt-get install python-virtualenv

If you are not familiar with the use of a virtualenv then can have a look at
the `userguide of virtualenv <https://virtualenv.pypa.io>`_.

.. _installpostgresql:

********
Postgres
********
Ringo requires a `Postgresql <https://www.postgresql.org>`_ database. Further
we need some development packages because python postgres driver will be build
on :ref:`bootstrapenv`.

Install Postgres the package manger::

        apt-get install postgresql
        apt-get install postgresql-server-dev-9.5 python-dev gcc

Now create a user in the database. This user should have the same name as the
user who is going to run the application later.  This user will be used to
connect to the database.  The uses must be allowed to create new databases. In
this example we create a user *ringo*::

        su postgres
        createuser -d ringo

This user and his credentials are later needed in den `*.ini` application
configuration to configure the db connection.

Even that Ringo uses a ORM such as SQLAlchemy Ringo currently relies on a
Postgresql database. This is mainly for historical reasons: There has been
times where the default database of Ringo was `SQlite
<http://www.sqlite.org>`_. But migrating the schema of the database during the
developement was a huge pain, because of its limited support of SQL commands.
Hower maybe this will change again in the future. If you want to help please
have a look at `the related issue
<https://github.com/ringo-framework/ringo/issues/23>`_


***************
Python3 support
***************
I'm sorry. Python 3 is currently not supported. Your help to port Ringo for
Python 3 is welcome!

##########
Quickstart
##########

.. _bootstrapenv:

*********************************
Bootstrap Development Environment
*********************************

Do::

        apt-get install git
        curl -O https://raw.githubusercontent.com/ringo-framework/ringo/master/bootstrap-dev-env.sh
        sh bootstrap-dev-env.sh ringo

Structure::

        ringo
        |-- env
        |   |-- ...
        |   `-- bin
        `-- lib
            |-- brabbel
            |-- formbar
            `-- ringo



*********************
A minimal Application
*********************

Activate the virtualenv and change into you development environment::

        cd /path/to/your/development/environment
        source env/bin/activate

Create a fresh application based on a ringo project template::

        pcreate -t ringo foo
        mv foo src
        cd src
        python setup.py develop

Optional: Setup the database connection in the generated *development.ini*
file and configure the user you created in the process of installing
:ref:`installpostgresql`. If you followed the instructions you're done and no
further action is needed. However here is an example how to change the
connection to database.::

        -sqlalchemy.url = postgresql://@/foo
        +sqlalchemy.url = postgresql://user:password@localhost/foo 

Create a new database for your application and initialise the database using
the :ref:`clidb`::

        createdb foo
        foo-admin db init

Start the application::

        pserve --reload development.ini


#########
Tutorials
#########

.. _add_modul:

***************
Add a new modul
***************
Please make sure you understand the concept of :ref:`modules` before adding a
new module. In some cases it might be sufficient to only :ref:`add_view`.

First you create the initial files and a migration to "install" the module in
your application using the :ref:`climod` command. Please use the singular form
of the name of the module::

        ringo-admin modul add <modulname in singular form>

This will generate a bunch of files:

 * A model file
 * A XML configuration for the form configuration
 * A JSON configuration for the overview/listing configuration
 * A migration file to install the modul.

Upgrade the database to apply the generated migration and to install the
initial data for the module by using the :ref:`clidb` command::

        ringo-admin db upgrade

The module is now installed and ready for use. Restart your application. The
module should now be listed in the main menu. You can already call all CRUD
actions of the module, but for now no data is saved as the model of the module
is basically empty. So its time to add some fields to your new module.


******************
Extending a module
******************

Add new fields
==============
Adding new fields to the module means finally means adding new fields to the
model of the module and finally to do a migration.

There are two ways to to this:

 1. You do all the work on your own and add the fields directly in the model file of your module. If you want to choose this way I recommend reading the `SQLAlchemy documentation on Decalaritve Mapping <http://docs.sqlalchemy.org/en/latest/orm/mapping_styles.html#declarative-mapping>`_

 2. You focus on developing the form of the module and let Ringo generate the relevant part of the model your you. This way you only need to copy and paste the generated model code into your model. If you choose this way than you should become familiar with the :ref:`formconfig` (Which is a crucial part of Ringo development anyway).

Whatever way you choose it finally ends in the generating a migration file
and upgrading the database using the :ref:`clidb` command::

        ringo-admin db revision
        ringo-admin db upgrade

Build relations between modules
===============================
Adding a relation between two modules is usually done in two steps:

 1. Add fields to the model for the foreign key and add an ORM relation.
 2. Migrate the database.

Here is a short example from `ringo/model/user.py`::

        class User(BaseItem, Owned, Base):
                ...
                sid = sa.Column(sa.Integer, sa.ForeignKey('user_settings.id'))
                # user_settings is the name of the table in the database for
                # the settings. This field refers to the id column of that
                # table.
                ...
                settings = sa.orm.relationship("UserSetting", uselist=False,
                                               cascade="all,delete")
                # UserSetting is the name of the Python class to which the
                relation is set.

If you want to use this relation later in forms than you must refer to the
`settings` attribute of the User and **not** to foreign key.

There is nothing specific in Ringo on adding a foreign key and a relation to
the model so all relevant information can be found in the `ORM
documentation <http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html>`_ of SQLAlchemy.

.. tip::
        If you have a bidirectional relation between to modules we recommend
        to set up the ORM relation in both modules instead of using the
        *backlink* feature of SQLAlchemy. Writing to relations tends to be
        better readable esspecially when it comes to cascading rules.

.. _add_mixin:

Extend modul with a mixin
=========================
Please make sure you understand the concept of :ref:`mixins` before extending the module. In some cases it might be sufficient to only :ref:`add_view` or :ref:`add_action`.


.. index::
   single: CRUD

.. _add_action:

Add a new action to a modul
===========================
Initially each module has only the default :ref:`crud` actions available.
However the module can be extended by adding a new specific action.

Setup breadcrumbs
=================
Breadcrumbs are a great way to help users to navigate through a nested set of
related modules and alway show them where they are.

Ringo can show breadcrumbs. They are optional. If you want them you need to
configure a `Sitemap`. The sitemap is build in the *__init__.py* file of your
application::

        from ringo.lib.sitetree import site_tree_branches
        sitetree = { your sitetree configureation goes here }
        site_tree_branches.append(sitetree)

For a detailed description on how to build a see the documentation of the
sitetree module.

Sitetree module
---------------
.. automodule:: ringo.lib.sitetree


.. _formconfig:

******************
Form configuration
******************
Form configuration is done in XML files. Configurations are stored in
`<yourproject>/views/forms/` folder.

Ringo uses the `formbar <http://formbar.readthedocs.io/en/latest/>`_ library
for form handling.it gives you plenty of nice features like easy design,
validation, conditional fields and rule expressions to only name some of them.

.. tip::
        You can easily add fields to the form, change the layout and see the
        results immediately when you reload the page. This is a great help
        when you design forms. The only restriction to this is storing the
        data and doing 

Using formbar
=============
Please have a look into the `formbar documentation <http://formbar.readthedocs.io/en/latest/>`_ to learn how to configure forms using formbar and check the forms in `ringo/views/forms` for some examples.

Generate model fields
=====================
After you have added new fields to the form you need to add those fields to
the model too. Ringo provides a small helper command for this which will
generate the relevant fields from the given form for your model::

        ringo-admin modul fields <name of modul in plural form>

This will print some code to *stdout* which can be pasted into the model of
the module.

Don't forget to generate migration and upgrade the database::

        ringo-admin db revision
        ringo-admin db upgrade

Ringo specific renderer
=======================
Ringo comes with some specific renderers which extends the default renderers
of formbar. They usually are aware of accessing to Ringo specific attributes
like permissions checks e.g.

Checkbox
--------
.. autoclass:: ringo.lib.renderer.form.CheckboxFieldRenderer

Dropdown
--------
.. autoclass:: ringo.lib.renderer.form.DropdownFieldRenderer

Links
-----
.. autoclass:: ringo.lib.renderer.form.LinkFieldRenderer

Listings
--------
.. autoclass:: ringo.lib.renderer.form.ListingFieldRenderer

State
-----
.. autoclass:: ringo.lib.renderer.form.StateFieldRenderer


Writing a new renderer
======================
Ringo let you easily define your own custom renderer. Custom renderers are
used to display the data in a free defined form. You can define new input
elements or present you data in diagram e.g.

Writing an using custom renderers is done in two steps:

 1. You write the renderer and templates
 2. You bind in the new renderer in the application

Renderer part
-------------
First create a new renderer by ineriting from an existing one. Formbar and
Ringo already provide some renderers which can be used. Renderers are usally
located in `lib/renderer.py` or `lib/renderer/form.py`.

Here you see the code for a simple renderer::

        import os
        import pkg_resources
        from mako.lookup import TemplateLookup
        from formbar.renderer import FieldRenderer
        from ringo.lib.renderer.form import renderers

        # We need to configure the template lookup system and "register" a new
        # location of the templates. Mako will search in this locations for
        # templates to render.
        base_dir = pkg_resources.get_distribution("namofapplication").location
        template_dir = os.path.join(base_dir, 'nameofapplication', 'templates')
        template_lookup = TemplateLookup(directories=[template_dir],
                                         default_filters=['h'])

        # Now create your renderer. And define the template which is used on
        # rendering.
        class MyFieldRenderer(FieldRenderer):

            def __init__(self, field, translate):
                FieldRenderer.__init__(self, field, translate)
                self.template = template_lookup.get_template("path/to/field/template.mako")


        # Finally register the template in ringo to make the renderer known in
        # formbar.
        renderers['myrenderer'] = Myfieldrenderer

A template looks like this::
        
        <div id="${field.id}">
                I'm the body of your field with name ${field.name}. In
                ${field._form} which is there to render fields of
                ${field._form._item} with renderer ${field.renderer}. Add
                content here.
        </div>


View part
---------
Using the new renderer is about configuring the renderer for an entity::

        <entity ...>
                <renderer type="myrenderer"/>
        </entity>

The type of the renderer is the name of the renderer under which it has been
registered in ringo.



**********************
Overview configuration
**********************
Fields
======
Sorting
=======
Filters
=======

.. _add_view:

**************
Add a new view
**************

********************
Custom authorisation
********************
If you need to change the way Ringo builds the ACL on default you can change this behavior by 
overwriting the ``_get_permissions`` class method of the BaseItem in your model.

.. todo::
        Give an example

.. todo::
        Write about inheritance of authorisation


***********************
All about customization
***********************
How Ringo overwrites the defaults
=================================

Change default templates
========================
Typical default templates are the `about`, `index` and `contact` templates.

Add custom logo
===============

Custom CSS
==========

Custom Javascript
=================


##############
Under the hood
##############

.. image:: images/applayers.png
   :alt: Layermodel of Ringo.

Ringo is a Pyramid based application which can be extended to build your own
applications. This is a layered architecture where Pyramid brings in the basic
functionality like session handling and handling requests and responses in web
applications.  Ringo sits on top of Pyramid and provides commonly used
functionality often used in modern web applications.

.. note::

   Ringo is also a standalone application. You do not need to build another
   application on top of ringo to get something working to get an impression
   of ringo or start developing. Ringo is under steady development. This is a
   benefit if you use Ringo as base for your application. Your application
   will get bug fixes, new features or improved functionality in most cases by
   simply updating Ringo to a new version.

Ringo itself uses some external libraries to provide some of its
functionality. E.g the formbar library is used to build all forms and do
validation. The access to the database is done with the ORM SQLAlchemy.

A ringo based application is another pyramid based application which basically
extends ringo. See `Exending An Existing Pyramid Application
<http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/extending.html>`_
for more details on how this is done.

All this magic is already done in a pyramid scaffold which comes with ringo.
Using this scaffold will create an application which uses ringo functionality
by simply importing it at the right places and take care the basic
configuration is done in the proper way.

.. _modules:

*******
Modules
*******
The term "Module" is central and often used in ringo. Therefore it is important
to understand what a module is.

In short: Ringo's functionality is the sum of all modules
functionality. Ringo or a ringo based application can be extended by adding
new modules. If there is any data in the application which needs to be created
by the user and stored permanently in the database it is very likely done
within a modul.

**Example:** Think of an application to organise your orders in a shopping
application e.g. So you will have to store customers, articles, orders, prices,
addresses etc. Each of those will be its own modul.

.. image:: images/modules.png
   :alt: Schema of a module.

A module provides the infrastructure to work with a certain type of data in a
web application. Where certain type of data means users, files, movies etc.
rather than integers or datevalues. Lets call them items from now on.

Basically a module consists of

 * a model for the items you want to work with
 * views to handle incoming request and generating the proper responses for
 * templates which define how the pages in the application will look like. 
 * configuration files to define how the forms and overview tables will look like.

.. _crud:

CRUD actions
============
Modules provide actions which can be used to manipulate the item of a module.
Ringo provides some basic CRUD [#]_ actions which are available on default for every module.

* Create: Create new items.
* Read: Show the item in detail in readonly mode.
* Update: Edit items of the module.
* Delete: Deleting items.
* List: Listing all items of the module. This is slightly different to the action to read a single item.
* Import (CSV, JSON)
* Export (CSV, JSON)

.. [#] CRUD means: Create, Read, Update, Delete

**********
Extensions
**********

Available extensions
====================

.. _mixins:

******
Mixins
******
.. automodule:: ringo.model.mixins

Available mixins
================

.. _mixin_meta:

Meta
----
.. autoclass:: ringo.model.mixins.Meta

.. _mixin_owned:

Owned
-----
.. autoclass:: ringo.model.mixins.Owned

.. _mixin_nested:

Nested
------
.. autoclass:: ringo.model.mixins.Nested

.. _mixin_logged:

StateMixin
----------
.. autoclass:: ringo.model.mixins.StateMixin

********
Security
********
Security is an important aspect of ringo. This chapter will describe the
permission system and explains how ringo handle common security threats.

.. _permissionsystem:

Permission System
=================
The permission system addresses two basic questions:

1. **Who is allowed** to access some item in general and
2. **What is allowed** for the user to access, in case he is generally allowed
   to access the item.

To answer these two questions the permission system of Ringo is a combination
of concepts of the permission system known from the `Unix file system  <http://http://en.wikipedia.org/wiki/File_system_permissions>`_ and a
`roles based permission system <http://http://en.wikipedia.org/wiki/Role-based_access_control>`_.

.. image:: images/permissions.png
   :width: 500
   :alt: Activity diagram of the permission check.

The Unix file system part answers the first question: Who is allowed? Therefor
every item in the system inherited from the :ref:`mixin_owned` stores
information to which owner and which group it belongs to. Only the owner,
members of the group or users with an administrational role are granted access
to the item in general.

After the permission to access the item in general is allowed, the role bases
system answers the second question: What is allowed. The permission system
will now check which :ref:`roles` the users have and which actions are allowed for
these roles.

If the user is the owner of the item, or is member of the items group, then
all permissions of the users roles will be applied.

.. note::
        Currently there is no anonymous access to the item. See Issue61 in the
        ringo bugtracker. A workaround might be to setup a user group with
        all users of the system and assing the needed roles to it. Then set
        this group as the item group.

See :ref:`authorisation` for more details on this.

.. _authentification:

Authentification
----------------
Authentication is done once in the login process. If the user has logged in
successful an auth cookie is saved. From then on the user object is loaded
from the database on every request with the roles and groups attached to the
user.  This user object is used later for the Authorisation. If the user is
not logged in the user object is empty.

The authentification has a default timeout of 30min. The timeout will be reset
after every new request of the user. The timeout can be configured in the
application configuration bei setting the 'auth.timeout' config variable.

.. _authorisation:

Authorisation
-------------
The permission system in Ringo uses the Pyramid `Pyramid Authorisation and
Authenfication API <http://docs.pylonsproject.org/projects/pyramid/en/latest/api/security.html>`_

Authorisation is done on every request. The authorisation will check if the
user is allowed to access the requested resource.

A resource is an url or an item which is accessed by calling the url in your
application.  In all cases this resource is build from a resource factory for
every request.  Every resource will have an ACL which determines if the user of
the current request (See :ref:`authentification`) is allowed to access the
resource.

Ringo's part in the authorisation process is to build the ACL. This ACL is
then used by the Pyramid security API. Therefor ringo implements helper
functions to build ACL lists which model the ringo permission system.

See `Adding Authorization tutorial
<http://docs.pylonsproject.org/projects/pyramid/en/latest/tutorials/wiki2/authorization.html>`_
for more information how things work in general under the hood.

See :ref:`api-security` for documentation on helper functions used to build
the ACL.

Security measurements
=====================
Ringo has protection against common threads of webapplication included.

CSRF-Protection
---------------
To protect against CSRF attacks ringo follows the recommodation of `OWASP
<http://url>`_ and adds a synchroniser token to each form, which will be sent
and checked on each POST request. The token will be unique on every request.
GET requests in ringo are not protected as GET functions in ringo should be
idempotent and does not trigger expensive opertaions. Following this simple
philosophie on GET requests will make any further CSRF protection obsolete.

XSS-Protection
--------------
Ringo will add the following headers to protect the application against XSS attacks.

 * 'X-XSS-Protection': '1; mode=block',
 * 'X-Content-Type-Options': 'nosniff'

Further ringo provides an option to enable a contect CSP for further
protection. The CSP is disabled on default but can be enabled in the
application :ref:`conf_headers` configuration.

Clickjacking-Protection
-----------------------
Cookie and Session security
---------------------------

DOS-Protection
--------------
DOS protection is not handled by ringo. Protection against DOS-attacks should
be handled by the Reverse Proxy or Firewall.

***************
Basic DB Schema
***************
Below you see the basic schema of the ringo database. The schema only lists
some central tables which help to understand how the things are wired together
in ringo. The table colored orange `example` table in the top left is an
example for any other table which will store items of a modul.
Every item of an item has a reference to the module it belogs to. Further the
current example has a reference to a user and a usergroup which defines the
ownership [#]_ per item is is important for the authorisation.

.. image:: images/database.png
   :alt: Basic database model.

Let us begin with the `modules` table. This table will store information on
all available modules in the system. It basically stores the configuration per
modul.  As described in the :ref:`modules` section each modul has
(:ref:`module_actions`) which are stored in the `actions` table. The NM-table
`nm_actions_roles` define which `roles` are allowed to use the actions in the
module. See :ref:`permissionsystem` for more information on how the
:ref:`authorisation` is implemented in ringo.

The `users` table stores all the users in ringo. The users table only holds
minimal data which is required for authentification and authorisation.
Additional information like the name, email etc. is stored in the `profiles`
table. Every user has a profile.

Users can be organised in groups using the `nm_user_groups` table. All
usergroups are stored in the `usergroups` table. Roles can be assigned to
usergroups and users. This is done with the NM-table `nm_user_roles` and
`nm_usergroup_roles`.

The table `user_settings` and `password_reset_request` are helper tables to
save user settings like saved search queries or store the tokens to trigger
the password reset.

.. [#] The ownership feature can be added by using the :ref:`mixin_owned`
   mixin.

********************
States and Workflows
********************
.. automodule:: ringo.model.statemachine

#############
Configuration
#############
The application can be configured by setting values in the
``ini`` file. Ringo provides some helper methods to give directly access to
some of the configuration options.

***********
Application
***********
Helper methods giving access to the configuration options are available in the `appinfo` module.

.. automodule:: ringo.lib.helpers.appinfo
   :members: get_app_mode, get_app_title, get_app_inheritance_path


Title
=====
The name of the application used at various places in the application
can be configured with the following varible.

* app.title = Application name 

The title is available using the :func:`get_app_title` function.

.. _config_app_base:

Application Base
================
Optional. Usually a ringo based application is directly based on ringo.
So the default inheritance path of your application is foo->ringo (in
case your application package is called "foo").

* app.base = Default is not set

If your application is based on another ringo based application you can
configure the name of the application here. Setting this configuration
will modify the inheritance path of the application.

The inhertance_path is available using the :func:`get_app_inheritance_path`
function.

Example:
The current application package is named "foo". "foo" is based on "bar". And
"bar" is based on "ringo". The inheritance path is foo->bar->ringo.

This has consequences for the loading of form and table configurations.
When trying to load form or table configuration ringo will iterate over
the inheritance path and try to load the configuration from each
application within the inheritance path.

Application Mode
================
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

Cache
=====
You can configure to cache the loaded configurations for the form
configs. This is usefull in production mode for a significant speed up
when loading large forms with many rules and conditionals.

* app.cache.formconfig = true

The default is not to cache the configuration.

Testing mode
============
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

******
Layout
******

Default Overview complexity
===========================

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
=============
You can configure to show a session timer widget in the header of the
application. The session timer will show the time left in the current session
and provides a button to refresh the session.

* layout.show_sessiontimer = true.
  
Default is false, no widget is shown.

The time of the session timer is configured in :ref:`admin_autologout`.

Login Info
==========
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


Contextmenu
===========
You can configure if the context menu will be displayed in the detailed item
view. For simple applications this menu might provide too much functionallity
which tends to be confusing to other users. So you can completeley disable it.

.. image:: ../screenshots/ui/contextmenu.png

* layout.show_contextmenu = true

Default is true, so the menu is shown.

.. note::
   
   This setting only applies for users who does not have the admin role!
   Admins will always see the contextmenu available. Please not if your
   disable the menu the users will loose access to some default actions like
   changing the ownership. 


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

****************
Authentification
****************
Authentication is stored with in a auth_tkt cookie.  See `Cookie options on
<http://docs.pylonsproject.org/projects/pyramid/en/latest/api/authentication.html>`_
for more details. The settings as taken from the global :ref:`conf_cookies`
security settings.

.. _admin_autologout:

Autologout
==========
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
=======================================
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

********
Security
********

CSRF Protection
===============
To enable CSRF protection you can configure ringo to include a CSRF
synchronizer token to each form to protect POST request against CSRF attacks.

security.enable_csrf_check = true
        Defaults to `true`

However, for testing issues it might be useful to disable this feature.

.. _conf_cookies:

Cookies
=======
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
=======
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
=======
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

**********
DB Caching
**********
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


****
Mail
****
 * mail.host =
 * mail.default_sender =
 * mail.username =
 * mail.password =

*********
Converter
*********
.. note::
   To be able to use the converter you need to install the "converter" extra
   requirements. See ``setup.py`` file for more details.

 * converter.start = false
 * converter.pythonpath =

###############
CLI ringo-admin
###############
Use the following command to get general help on the available commands::

        ringo-admin help

.. important::
        All of the following commands will take the `development.ini`
        configuration file as their defautl configfile to retrieve
        informations like the db connection. Please make sure you set the
        correct config file before invoking the command to prevent operations
        on the wrong database!

.. _clidb:

**************
ringo-admin db
**************
Use the following command to get general help on the available commands::

        ringo-admin db help

Init database
=============
The database can be initiated with the following command::

        ringo-admin db init

Generate migration
==================
A new migration file can be generated with the following command::

        ringo-admin db revision

Upgrade database
================
The database can be upgraded by applying the migration scripts::

        ringo-admin db upgrade

Downgrade database
==================
The database can be downgraded by removing the last migration scripts::

        ringo-admin db downgrade 

Export data
===========
The data of a specfic module can be exported in a fixture by invoking the
following command::


        ringo-admin db savedata <modulname> > fixture.json

Importing data
==============
The data of a specfic module can be imported in a fixture by invoking the
following command::

        ringo-admin db loaddata --loadbyid <modulname> <fixture>

This will load the data in the fixture and insert or update the items in the
database. Deleting items is not supported.

The option *--loadbyid* changes the mode how exiting items in the database are
loaded for either update or, in case there is no record found, creating a new
item. The default is loading mechanism is loading by  the items UUID. But this
isn't practical for loading initial data.

Fixing Sequences
================
After loading data into the database it is often needed to fix the sequences
in the database to make the incremental counters work correct::

        ringo-admin db fixsequence

****************
ringo-admin user
****************
Use the following command to get general help on the available commands::

        ringo-admin user help

Set password
============
The password of a given user can be changed/set by invoking the following
command::

        ringo-admin user <login> --password <password>

The `password` parameter is optional. If not given ringo will autoegenerate a
new password for you.

********************
ringo-admin fixtures
********************
Initial data can inserted in the application by loading fixtures. Fixtures are
basically the export of the item of a model in JSON format. Actually the whole
loading and saving data is implemented by using the importer and exporter.

.. note::
   Please note that you must take care to load the fixtures in correct order,
   because to keep the integrity of the database.

The folder for the fixtures should be named *fixtures* and located in the
application folder.

The default location of the fixtures is the fixtures directory of your
application.  You can define an alternative path the the fixtures when
invoking the load or save command by providing the `--path` option.

There are some naming conventions. Fixtures should be namen
'NN_modulname.json'. NN means is used to order the fixtures and determines in
which order the fixtures will be loaded. The modulname configures for which
module the fixtures contains data. The name of the module name is identical
with the name of the database table which has a appended "s". E.g the *user*
modul becomes to *users*. This is even true if the appended "s" is written
wrong.

Use the following command to get general help on the available commands::

        ringo-admin fixtures help

Load data
=========
By invoking the following command::

        ringo-admin fixtures load

all fixtures in the fixtures directory will be loaded and inserted in the
database.

Using the `--path` allows to define a alternative path to the fixture files.

Save data
=========
By invoking the following command::

        ringo-admin fixtures save

all fixtures in the fixtures directory will be loaded and the data for each
modul will be written into the fixture.

Using the `--path` allows to define a alternative path to the fixture files.


.. _climod:

*****************
ringo-admin modul
*****************
Use the following command to get general help on the available commands::

        ringo-admin modules help

Add new modul
=============
By invoking the following command::

        ringo-admin modul add <modulname in singular form> 

A new modul will be added to your application. See :ref:`dev_modules` for more
details.

Generate model fields from form config
======================================
By invoking the following command::

        ringo-admin modul fields <name of the modul>

The python code with the SQLAlchemy model will be generated. The code can be
pasted into the model.

***************
ringo-admin app
***************

.. todo:: Write me.

######################
Application Deployment
######################

.. _deployment_subpath:

****************************************************
Running the application in a different path than "/"
****************************************************
If the application is hosted in a subpath, than need to make sure that the
`SCRIPT_NAME` and `PATH_INFO` variable are set correct, as both variables are
crucial for a pyramid application to handle the requests and build urls using
the `request.route_*` functions correct. 

Ideally those variables are set before the request enters your application.
This means you do this directly in the serving component. The configuration of
the server components are out of scope of this documentation. Please refer to
the documentation of your server component!

But instead of transforming the variables directly in the server you can also
configure your application to do so. This way you get indepentend from the
server, with the drawback that the information about the path need also be set
in your application configuration. Here comes the following options.

.. rubric:: Use a "prefix" middleware

All requests are routed through another middleware which will modify the
`SCRIPT_NAME` and `PATH_INFO`. Here is how to configure it::

        [filter:paste_prefix]
        use = egg:PasteDeploy#prefix
        prefix = /myapp

        [pipeline:main]
        pipeline =
           paste_prefix
           myapp

        [app:myapp]
        ...

.. rubric:: Build a "composite" application

Originally intended to map differen URLs to different
applications/services (SAS) this can be also used to get the SCRIPT_NAME and
PATH_INFO right. See `Paste documentation for urlmap
<http://pythonpaste.org/deploy/index.html?highlight=urlmap>`_ for more
informations. Here is a short example to get the idea::

        [composite:main]
        use = egg:Paste#urlmap
        # This is the mapping of the path /myapp to an application named
        # myapp 
        /myapp = myapp
        ...

        [app:myapp]
        ...

********
Examples
********

uWSGI & Nginx
=============
Make sure your have installed the follwing additional packages in your virtualenv:

 * uWSGI
 * PasteDeploy (needed to be able to read the application configuration from
   the ini file)
 * PasteScript (needed to get the logging configured based on the setting in
   the ini file)

Add the following into your ini file::

        [uwsgi]
        master = true
        socket = /tmp/uwsgi.sock
        virtualenv = /path/to/virtualenv

        # PERMISSIONS
        # Make sure that ngnix has permission to read and write to the socket.
        # You can use one or more of the following options:
        #chmod-socket =
        #uid =
        #gid =

        # DAEMONIZE
        # Send it in the background. If daemonize is set it wil log its output
        # into given logfile
        #daemonize = ./uwsgi.log
        #pidfile = ./uwsgi.pid

        # LOGGING
        # paste-logger =
        # Yes, there is no argument for the paste-logger.

Some notes on logging:

1. The Logfile must be writeable for the uWSGI process!

2. Make sure that your logging configuration of the application does not
   contain any place holders like "%(here)s". They are not valid in the scope
   of uWSGI.

3. On default the log of the uwsgi process will contain the requests as same
   as the logging from the application. If you want to separate this I advice
   you to disable to console logging in your pyramid application. Instead use
   a FileLogger which will log the logging in the application to a different
   location. See `Pyramid logging documentation for more details
   <http://docs.pylonsproject.org/projects/pyramid//en/latest/narr/logging.html>`_

Add the following into your ngnix configuration::

        location / {
            uwsgi_pass  unix:///tmp/uwsgi.sock;
            include     uwsgi_params;
        }

Start the uwsgi server by invoking the following command::

        uwsgi --ini-paste--logged development.ini

For debugging purpose I recommend to disable daemonizing in the uWSGI
configuration.


Nginx as Reverse Proxy
======================
Add the following into your ngnix configuration::

        location / {
            proxy_set_header        Host $http_host;
            proxy_set_header        X-Real-IP $remote_addr;
            proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header        X-Forwarded-Proto $scheme;
            proxy_pass http://localhost:7450;

        }
