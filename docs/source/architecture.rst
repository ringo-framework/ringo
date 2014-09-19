############
Architecture
############
The architecture of ringo is shown below.

.. image:: images/applayers.png
   :alt: Schema of a modul.

Ringo is a Pyramid based application which can be extended to build your own
applications. This is a layered architecture where Pyramid brings in the basic
functionality like session handling and handling requests and responses in web
applications.  Ringo sits on top of Pyramid and provides commonly used
functionality often used in modern web applications. See :ref:`Features` for
an overview.

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
configuration is done in the proper way. See
:ref:`create_ringo_based_application` for information on how to create an
application using this scaffold.

Filesystem
**********
Ringo is organised in the following file layout::

        .
        ├── alembic
        ├── docs
        └── ringo
           ├── lib
           ├── locale
           ├── model
           ├── scaffolds
           ├── scripts
           ├── static
           │   ├── bootstrap
           │   ├── css
           │   ├── images
           │   └── js
           ├── templates
           │   ├── auth
           │   ├── default
           │   ├── internal
           │   ├── mails
           │   └── users
           ├── tests
           ├── teens
           └── views
               ├── forms
               └── tables

alembic
   Migration scripts for the database.
docs
   Documentation of ringo. This documentation.
ringo
   The ringo application.
ringo/lib
   Helper libraries. lenderers, validators, security related functions.
ringo/locale
   i18n Internationalisation
ringo/model
   Models for users, usergroups, modules, roles etc.
ringo/scaffolds
   A scaffolds includes the boilerplate code to create a ringo based application.
ringo/scripts
   Administration commands and scripts.
ringo/static
   Static files like images or CSS and JS scripts.
ringo/templates
   Templates for various parts of the application. Templates in the internal
   folder are used internally by customs form or overview renderers. The
   default folder has the templates for default CRUD actions and confirmation dialogs.
ringo/tests
   Unit tests and behaviour driven tests. See :ref:`tests` for more details.
ringo/tweens
   Middleware like code. Used to modify headers in response objects.
ringo/views
   Views with the business logic for the application. 
ringo/views/forms
   Configuration of forms for each modul.
ringo/views/tables
   Configuration of overview tables for each modul.




Database
********
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


.. _modules:

Modules
*******
The term "Module" is central and often used in ringo. Therefore it is important
to understand what a module is. This section tries to explain that.

.. image:: images/modules.png
   :alt: Schema of a module.

You can think of a module in the way that it provides the infrastructure to
work with a certain type of data in a web application. Where certain type of
data means users, files, movies etc. rather than integers or datevalues. Lets
call them items from now on.

A module will have a model for the items you want to work with. It will include
views to handle incoming request and generating the proper responses for
users. Further it has templates which define how the pages in the application
will look like. Finally there are configuration files to define how the forms
and overview tables will look like.

Ringo already come with many modules. One module per item. There is a module
for the user management, a module for appointment and so on. There is also a
module to handle the modules itself. So we can say in general: ringos
functionality is the sum of all modules functionality. Ringo or a ringo based
application can be extended by adding new modules.  Fortunately you will not
need to create this infrastructure for you own. See :ref:`add_modules` for
more information.

Each module has a common set of configuration options which can be done
directly in the web interface. See the modules entry in the administion menu
for more information.

Modules provide actions which can be used to manipulate the item of a module.
Ringo provides some basic CRUD [#]_ actions which are available on default for every module.

* Create: Create new items.
* Read: Show the item in detail in readonly mode.
* Update: Edit items of the module.
* Delete: Deleting items.
* List: Listing all items of the module. This is slightly different to the action to read a single item.
* Import (CSV, JSON)
* Export (CSV, JSON)

Every time you want to do something different to your items you will likely
want to implement another action for the module. See :ref:`add_action` for
more details how to add actions to a module.

.. [#] CRUD means: Create, Read, Update, Delete

Extensions
==========
.. automodule:: ringo.lib.extension


Mixins
======
.. automodule:: ringo.model.mixins

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

Logged
------
.. autoclass:: ringo.model.mixins.Logged

.. _mixin_versioned:

Versioned
---------
.. autoclass:: ringo.model.mixins.Versioned

.. _mixin_state:

StateMixin
----------
.. autoclass:: ringo.model.mixins.StateMixin

Commented
---------
.. autoclass:: ringo.model.mixins.Commented

Tagged
------
.. autoclass:: ringo.model.mixins.Tagged

Todo
----
.. autoclass:: ringo.model.mixins.Todo

.. __mixin_printable:

Printable
---------
.. autoclass:: ringo.model.mixins.Printable

Event Handlers
==============
Each modul can implement one of the following event handlers to realize
automatic modifications of the items:

 * create_event_handler(request, item, \**kwargs)
 * update_event_handler(request, item, \**kwargs)
 * delete_event_handler(request, item, \**kwargs)

The functions will be called for all base classes of the item
automatically in the base controller if the specific view function for
the event (update, create, delete) is excecuted.

Some of the Mixin classes do already have some predefined event_handlers
configured.

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

There are currently two ways a user can be equiped with permissions:

1. If the user is the owner of the item, or is member of the items group, then
all permissions of the users roles will be applied.

2. If the user is member of the items group, then the permissins of the group
will additionally be applied.

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


States and Workflows
********************
.. automodule:: ringo.model.statemachine

For detailed descriptione of the involved classes see API documentation of :ref:`api-statemachine`

