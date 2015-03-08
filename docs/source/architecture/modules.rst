.. _modules:

Modules
*******
The term "Module" is central and often used in ringo. Therefore it is important
to understand what a module is. This section tries to explain that.

.. image:: ../images/modules.png
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

.. image:: ../images/database.png
   :alt: Basic database model.

Ringo uses the term "Modul" to describe different data (data types) in your
application.  Ringo comes with some predefined modules for users, usergroups,
roles and the modules itself.  Each of those moduls provide an interface with
basic CRUD functionality of work witch items of a modul.

.. image:: ../images/applayers.png
   :alt: Schema of a modul.

Moduls also define some meta data on the data like which actions (Create,
Read, Update, Delete...) are available, labels, visibility etc.  Further the
authorisation is bound to the moduls too and defines and which users are
allowed to use the configured actions.

.. image:: ../images/modules.png
   :alt: Schema of a modul.

If there is any data in the application which needs to be created by the user
and stored permanently in the database it is very likely done within a modul.

Example:: Think of an application to organise your orders in a shopping
application e.g. So you will have to store customers, articles, orders, prices,
addresses etc. Each of those will be its own modul.

See :ref:`commands` for more information on how to add new moduls to your
application.

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

StateMixin
----------
.. autoclass:: ringo.model.mixins.StateMixin

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
