************
Architecture
************
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

A ringo based application is another pyramid based application which basically extends ringo. See `Exending An Existing Pyramid Application <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/extending.html>`_ for more details on how this is done.

All this magic is already done in a pyramid scaffold which comes with ringo. Using this scaffold will create an application which uses ringo functionality by simply importing it at the right places and take care the basic configuration is done in the
proper way. See :ref:`create_ringo_based_application` for information on how
to create an application using this scaffold.

Modules
=======
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
for the user management, a module for appointment and so on. There is also a module to handle the modules itself. So we can say in general: ringos functionality is the sum of all modules functionality. Ringo or a ringo based application can be extended by adding new modules.  Fortunately you will not need to create this infrastructure for you own. See :ref:`add_modules` for more information.

Each module has a common set of configuration options which can be done
directly in the web interface. See the modules entry in the administion menu
for more information.





Filesystem
==========

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
ringo/views
   Views with the business logic for the application. 
ringo/views/forms
   Configuration of forms for each modul.
ringo/views/tables
   Configuration of overview tables for each modul.


Database
========

.. image:: images/database.png
   :alt: Basic database model.

Event Handlers
==============
Each class can implement one of the following event handlers to realize
automatic modifications of the items:

 * create_event_handler(request, item, \**kwargs)
 * update_event_handler(request, item, \**kwargs)
 * delete_event_handler(request, item, \**kwargs)

The functions will be called for all base classes of the item
automatically in the base controller if the specific view function for
the event (update, create, delete) is excecuted.

Some of the Mixin classes do already have some predefined event_handlers
configured.

Mixins
======
Mixins can be used to add certain functionality to the BaseItems. Mixins are
used in multiple inheritance. The ensure the the item will have all needed
fields in the database and have the right interface to work with the
functionality which is added by the mixin. Example::

        class Comment(BaseItem, Nested, Meta, Owned, Base):
            __tablename__ = 'comments'
            _modul_id = 99
            id = sa.Column(sa.Integer, primary_key=True)
            comment = sa.Column('comment', sa.Text)

            ...


The comment class in the example only defines the two fields 'id' and
'comment' but as it inherits from 'Logged', 'Meta' and 'Owned' it also will
have date fields with the creation and date of the last update, references to
the user and group which ownes the Comment. Further the 'Nested' mixin will
ensure the comments can reference each other to be able to build a hierarchy
structure (e.g Threads in the example of the comments).

Meta
----

Owned
-----

Nested
------

Logged
------

StateMixin
----------

Statemachine
============
Write me
