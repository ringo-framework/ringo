******************
CLI Administration
******************

Database
========
Init database
-------------
The database can be initiated with the following command::

        ringo-admin db init

Export data
-----------
The data of a specfic module can be exported in a fixture by invoking the
following command::


        ringo-admin db savedata <modulname> > fixture.json

Importing data
--------------
The data of a specfic module can be imported in a fixture by invoking the
following command::

        ringo-admin db loaddata --loadbyid <modulname> <fixture>

This will load the data in the fixture and insert or update the items in the
database. Deleting items is not supported.

The option *--loadbyid* changes the mode how exiting items in the database are
loaded for either update or, in case there is no record found, creating a new
item. The default is loading mechanism is loading by  the items UUID. But this
isn't practical for loading initial data.

Fixtures
========
Initial data can inserted in the application by loading fixtures. Fixtures are
basically the export of the item of a model in JSON format. Actually the whole
loading and saving data is implemented by using the importer and exporter.

.. note::
   Please note that you must take care to load the fixtures in correct order,
   because to keep the integrity of the database.

The folder for the fixtures should be named *fixtures* and located in the
application folder.

Fixtures are located in the fixtures directory of your application. There are
some naming conventions. Fixtures should be namen 'NN_modulname.json'. NN
means is used to order the fixtures and determines in which order the fixtures
will be loaded. The modulname configures for which module the fixtures
contains data. The name of the module name is identical with the name of the
database table which has a appended "s". E.g the *user* modul becomes to
*users*. This is even true if the appended "s" is written wrong.

Load data
---------
By invoking the following command::

        ringo-admin fixtures load

all fixtures in the fixtures directory will be loaded and inserted in the
database.

Save data
---------
By invoking the following command::

        ringo-admin fixtures save

all fixtures in the fixtures directory will be loaded and the data for each
modul will be written into the fixture.


Modules
=======

Add new modul
-------------

Generate model fields from form config
--------------------------------------

User
====

Set password
------------
