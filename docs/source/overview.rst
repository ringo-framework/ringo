########
Overview
########
Ringo is a small Python based high level web application framework build with
Pyramid. Ringo tries to make it very easy to build form based web application
to manage your data. Because ringo provides many basic features which are
often used in modern webapplications it greatly speeds up development. But it
is also flexible and offers many ways to configure the layout, behaviour and
workflow of your application. See the list of :ref:`features` for more
details.

Ringo comes with an application scaffold which can be used as a boilerplate for
your application development. See the :ref:`development` part for more details on how
to build a Ringo based application.

License
=======
Ringo is Free Software. It is licensed under the GPL license in version 2 or
later. See `<http://www.gnu.org/licenses/gpl-2.0>`_ for more details on the license.

.. _features:

Features
========
Ringo provides some basic features which are useful if you build your
web application:

 * Easy extendible and configurable modular architekture,
 * Basic actions for every modul including:
        - Search and sortable listing (storeable and configurable)
        - Basic CRUD actions
        - CSV, JSON import and export
 * Role based authorisation.
 * Authentication with email registration and password reminders
 * Powerfull statemachine to model workflows in moduls.
 * Layout and validation of forms using the `Formbar <https://pypi.python.org/pypi/formbar>`_ library
 * Logging of useractions
 * Versioning of forms (see what changed to the last version)
 * Widely configurable from the web UI.
 * Nice console client for various administration tasks.
 * ...

.. _installation_production:

Installation
============
Ringo is available in its latest stable version on `PyPi <https://pypi.org/toirl/ringo>`_::

The source code is also available on `Bitbucket <https://bitbucket.org/ti/ringo>`_ if you want to keep track of
the latest development version::

Please read the :ref:`development` section to learn how to setup Ringo based
application.

.. note::
   Ringo was developed within a Python 2.7.3 environment. Older versions will
   not work as Ringo uses some XML features only available in Python >= 2.7.3.
   Newer versions might work, but it is not tested.

Contact
=======
You can contact the author by his email address "torsten at irlaender dot de".
In case of bugs and feature requests please open a ticket on Bitbucket.
