********
Overview
********
Get an overview of Ringo. Know what it is, which features can be expected,
licensing and finally how to install it.

What is Ringo?
==============
Ringo is a small Python based high level web application framework build with
Pyramid . It provides basic functionality which is often used in modern web
applications. See the list of :ref:`features` for more details.

Ringo comes with an application scaffold which can be used as a boilerplate for
your application development. See the :ref:`development` part for more details on how
to build a Ringo based application.

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

.. _features:

Features
========
Ringo provides some basic features which are useful if you build your
web application based on Ringo:

 * Authentication with email registration and password reminders
 * Authorisation with a role based permission System
 * Basic CRUD actions
 * Layout and validation of forms using the `Formbar <https://pypi.python.org/pypi/formbar>`_ library
 * Support for caching expensive SQL queries
 * Regular expression based searching (storeable)
 * Sorting
 * User Profiles
 * Extendible, Configurable

.. _installation_production:

Installation
============
Ringo is available in its latest stable version on `PyPi <https://pypi.org/toirl/ringo>`_::

        pip install Ringo

The source code is also available on `Bitbucket <https://bitbucket.org/ti/ringo>`_ if you want to keep track of
the latest development version::

        hg clone https://bitbucket.org/ti/ringo
        cd ringo
        python setup.py install

You probably want to continue to read the :ref:`development` section to learn
how to setup Ringo based application.

Requirements
------------
Ringo was developed within a Python 2.7.3 environment. Older versions will not
work as Ringo uses some XML features only available in Python >= 2.7.3. Newer
versions might work, but it is not tested.

Contact
=======
You can contact the author by his email address "torsten at irlaender dot de".
In case of bugs and feature requests please open a ticket on Bitbucket.
