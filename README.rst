Ringo
=====
`Ringo` is a small Python based high level web application framework build with
Pyramid . It provides basic functionality which is often used in modern web
applications. See the list of features for more details.

Ringo comes with an application scaffold which can be used as a boilerplate for
your application development. See the development part in the documentation
for more details on how to build a Ringo based application.

In Ringo based applications Ringo plays the role of a base library which
provides basic functionality. In most cases this basic functionality should
fit the needs in easy usecases. If it fits not, then it can be extended and
configured to your need in an easy way.

Ringo is also a standalone application which is under steady development. This
is a benefit if you use Ringo as base for your application. Your application
will get bug fixes, new features or improved functionality in most cases by simply
updating Ringo to a new version.

License
=======
Ringo is Free Software. It is licensed under the GPL license in version 2 or
later. See `<http://www.gnu.org/licenses/gpl-2.0>`_ for more details on the license.

Features
========
Ringo provides some basic features which are useful if you build your
web application based on Ringo:

 * Authentication with email registration and password reminders
 * Authorisation with a role based permission System
 * Basic CRUD actions
 * RESTfull interface for CRUD operations.
 * Layout and validation of forms using the `Formbar <https://pypi.python.org/pypi/formbar>`_ library
 * Support for caching expensive SQL queries
 * Regular expression based searching (storeable)
 * Sorting
 * User Profiles
 * Extendible, Configurable

Documentation
=============
Documentation is available on `<http://pythonhosted.org/ringo/>`_


Getting Started
---------------
The fastest way to get an impression of Ringo`s core functionallity is to to
the following steps:

- cd <directory containing this file>

- $venv/bin/python setup.py develop

- $venv/bin/initialize_ringo_db development.ini

- $venv/bin/pserve development.ini
