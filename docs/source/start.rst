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
*************
Projectlayout
*************
.. _modules:

*******
Modules
*******

.. _crud:

CRUD actions
============

List
----
Create
------
Read
----
Update
------
Delete
------
Import
------
Export
------













**********
Extensions
**********

Available extensions
====================

.. _mixins:

******
Mixins
******

Available mixins
================

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

#############
Configuration
#############
###############
CLI ringo-admin
###############

.. _clidb:

**************
ringo-admin db
**************
****************
ringo-admin user
****************
********************
ringo-admin fixtures
********************

.. _climod:

*****************
ringo-admin modul
*****************
***************
ringo-admin app
***************
