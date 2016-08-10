******************
CLI Administration
******************

Use the following command to get general help on the available commands::

        ringo-admin help

.. important::
        All of the following commands will take the `development.ini`
        configuration file as their defautl configfile to retrieve
        informations like the db connection. Please make sure you set the
        correct config file before invoking the command to prevent operations
        on the wrong database!

Database
========
Use the following command to get general help on the available commands::

        ringo-admin db help

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

The default location of the fixtures is the fixtures directory of your
application.  You can define an alternative path the the fixtures when
invoking the load or save command by providing the `--path` option.

There are some naming conventions. Fixtures should be namen
'NN_modulname.json'. NN means is used to order the fixtures and determines in
which order the fixtures will be loaded. The modulname configures for which
module the fixtures contains data. The name of the module name is identical
with the name of the database table which has a appended "s". E.g the *user*
modul becomes to *users*. This is even true if the appended "s" is written
wrong.

Use the following command to get general help on the available commands::

        ringo-admin fixtures help

Load data
---------
By invoking the following command::

        ringo-admin fixtures load

all fixtures in the fixtures directory will be loaded and inserted in the
database.

Using the `--path` allows to define a alternative path to the fixture files.

Save data
---------
By invoking the following command::

        ringo-admin fixtures save

all fixtures in the fixtures directory will be loaded and the data for each
modul will be written into the fixture.

Using the `--path` allows to define a alternative path to the fixture files.

Modules
=======
Use the following command to get general help on the available commands::

        ringo-admin modules help

Add new modul
-------------
By invoking the following command::

        ringo-admin modul add <modulname in singular form> 

A new modul will be added to your application. See :ref:`dev_modules` for more
details.

Generate model fields from form config
--------------------------------------
By invoking the following command::

        ringo-admin modul fields <name of the modul>

The python code with the SQLAlchemy model will be generated. The code can be
pasted into the model.

User
====
Use the following command to get general help on the available commands::

        ringo-admin user help

Set password
------------
The password of a given user can be changed/set by invoking the following
command::

        ringo-admin user <login> --password <password>

The `password` parameter is optional. If not given ringo will autoegenerate a
new password for you.
