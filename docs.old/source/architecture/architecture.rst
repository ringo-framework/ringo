********
Overview
********
The architecture of ringo is shown below.

.. image:: ../images/applayers.png
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

A ringo based application is another pyramid based application which basically
extends ringo. See `Exending An Existing Pyramid Application
<http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/extending.html>`_
for more details on how this is done.

All this magic is already done in a pyramid scaffold which comes with ringo.
Using this scaffold will create an application which uses ringo functionality
by simply importing it at the right places and take care the basic
configuration is done in the proper way. See
:ref:`create_ringo_based_application` for information on how to create an
application using this scaffold.
