.. highlight:: shell

============
Installation
============

Ringo depends on some external libraries, like `Pyramid
<https://pylonsproject>`_, `SQLAlchemy <https://sqlalchemy.org>`_ and `Formbar
<https://formbar.readthedocs.io>`_. Pyramid is a very general open source
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

.. important::

        Python 3 is currently not supported. Your help to port Ringo for
        Python 3 is welcome!




The installation of Ringo is done in four steps. First we need to install
some :ref:`basicsupplement` which are needed later in the installation
process.
Second install a :ref:`venv` where all the python packages will be installed.
Third we need a DBMS and therefor install :ref:`installpostgresql`. Finally the last
step will :ref:`bootstrapenv`.

The following examples are tested on a Ubuntu 16.04 installation. 

.. _basicsupplement:

Basic supplement packages
-------------------------
*Curl* is used to fetch the bootstrap script which is used in the last step of
the installation.

*Git* is the SCM tool of choice for the Ringo development. To be able to
checkout the related packages during the bootstrap process you need to install
git.

Install all supplement packages::

        apt-get install curl git

.. _venv:

Virtualenv
^^^^^^^^^^
A `virtualenv <https://pypi.python.org/pypi/virtualenv>`_ is a isolated python
environment is used to install python packages independently from
your systems python environment. Using virtualenv you can setup unlimited number
of independent environments for your development.

Install the virtualenv using the package manger::

        apt-get install python-virtualenv

If you are not familiar with the use of a virtualenv then can have a look at
the `userguide of virtualenv <https://virtualenv.pypa.io>`_.

.. _installpostgresql:

Postgres
^^^^^^^^
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


Stable release
--------------

To install Ringo, run this command in your terminal:

.. code-block:: console

    $ pip install ringo

This is the preferred method to install Ringo, as it will always install the most recent stable release. 

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for Ringo can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/ringo-framework/ringo

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/ringo-framework/ringo/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/ringo-framework/ringo
.. _tarball: https://github.com/ringo-framework/ringo/tarball/master
