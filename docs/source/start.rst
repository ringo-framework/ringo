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
Please make sure you understand the concept of :ref:`modules` before adding a new module. In some cases it might be sufficient to only :ref:`add_view`

******************
Form configuration
******************
Using formbar
=============
Generate model fields
=====================
Ringo specific renderer
=======================
Listings
--------




**********************
Overview configuration
**********************
Fields
======
Sorting
=======
Filters
=======


.. _add_mixin:

*************************
Extend modul with a mixin
*************************
Please make sure you understand the concept of :ref:`mixins` before extending the module. In some cases it might be sufficient to only :ref:`add_view` or :ref:`add_action`.


.. index::
   single: CRUD

.. _add_action:

***************************
Add a new action to a modul
***************************
Initially each module has only the default :ref:`crud` actions available.
However the module can be extended by adding a new specific action.


.. _add_view:

**************
Add a new view
**************

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
*****************
ringo-admin modul
*****************
***************
ringo-admin app
***************
