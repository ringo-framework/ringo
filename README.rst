Ringo
=====
.. image:: https://drone.io/bitbucket.org/ti/ringo/status.png

Ringo is a small Python based high level web application framework build with
Pyramid. Ringo tries to make it very easy to build form based web application
to manage your data. Because ringo provides many basic features which are
often used in modern webapplications it greatly speeds up development. But it
is also flexible and offers many ways to configure the layout, behaviour and
workflow of your application. See the list of :ref:`features` for more
details.

Ringo comes with an application scaffold which can be used as a boilerplate for
your application development. See the development part in the documentation
for more details on how to build a Ringo based application.

License
=======
Ringo is Free Software. It is licensed under the GPL license in version 2 or
later. See `<http://www.gnu.org/licenses/gpl-2.0>`_ for more details on the license.

Features
========
Ringo provides some basic features which are useful if you build your
web application based on Ringo:

 * Easy extendible and configurable modular architekture,
 * Basic actions for every modul including:
        - Search and sortable listing (storeable and configurable)
        - Basic CRUD actions
        - CSV, JSON import and export
 * Role based authorisation.
 * Authentication with email registration and password reminders
 * Powerfull statemachine to model workflows in moduls.
 * Layout and validation of forms using the `Formbar <https://pypi.python.org/pypi/formbar>`_ library
 * Versioning of forms (see what changed to the last version)
 * Widely configurable from the web UI.
 * Nice console client for various administration tasks.
 * ...

Documentation
=============
The source of documentation comes with the source of ringo and can be found in the
"docs" folder. To generate the HTML version of the documentation please invoke the
following command::

        invoke docs

You need to have the sphinx package installed in order to generate the documentation.
A generated version of the documentation is available on
`<http://ringo.readthedocs.org/>`_


Getting Started
---------------
The fastest way to get an impression of Ringo`s core functionallity is to
start the standalone application of ringo with the following steps:

- $ hg clone https://bitbucket.org/ti/ringo

- $ python setup.py develop

- $ ringo-admin db init

- $ ringo-admin fixtures load

- $ invoke docs

- $ pserve development.ini
