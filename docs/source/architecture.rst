************
Architecture
************

.. image:: images/applayers.png
   :alt: Schema of a modul.

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

Modules
=======

.. image:: images/modules.png
   :alt: Schema of a modul.

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
