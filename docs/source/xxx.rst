Ringo
#####
This is the documentation of the Ringo software. After a short overview we
will explain the user interface and some basic concepts in Ringo.

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
later.

.. _features:

Features
========
Ringo provides some basic features which are useful if you build your
web application based on Ringo:

 * Authentication with email registration and password reminders
 * Authorisation with a role based permission System
 * Basic CRUD actions
 * Basic item sortable item listings
 * Layoutable forms
 * Extendable, Configurable

Installation
============
Ringo is available in its latest stable version on `PyPi <https://pypi.org/toirl/ringo>`_::

        pip install Ringo

The source code is also available on `Bitbucket <https://bitbucket.org/ti/ringo>`_ if you want to keep track of
the latest development version::

        hg clone https://bitbucket.org/ti/ringo
        cd ringo
        python setup.py install

Contact
=======
You can contact the author by his email address "torsten at irlaender dot de".
In case of bugs and feature requests please open a ticket on Bitbucket.

UI
**
Modules
*******
User
====

Usergroup
=========

Role
====

Modul
=====

Permission System
*****************
Authentification
================
Authorisation
=============

.. _development:

Development
###########
API
***
Tests
*****
Scaffolds
*********
Basic
=====
