***************
CLI ringo-admin 
***************
Use the following command to get general help on the available commands::

        ringo-admin help

.. important::
        All of the following commands will take the `development.ini`
        configuration file as their defautl configfile to retrieve
        informations like the db connection. Please make sure you set the
        correct config file before invoking the command to prevent operations
        on the wrong database!

.. _clidb:

ringo-admin db
==============
Use the following command to get general help on the available commands::

        ringo-admin db help

Init database
-------------
The database can be initiated with the following command::

        ringo-admin db init

Generate migration
------------------
A new migration file can be generated with the following command::

        ringo-admin db revision

Upgrade database
----------------
The database can be upgraded by applying the migration scripts::

        ringo-admin db upgrade

Downgrade database
------------------
The database can be downgraded by removing the last migration scripts::

        ringo-admin db downgrade 

.. index::
   single: Export
.. _clidb-export:

Export data
-----------
The data of a specfic module can be exported in a fixture by invoking the
following command::


        ringo-admin db savedata <modulname> > fixture.json

The default export format is JSON. You can change the export format to CSV by
providing the `--format` option.

Only values of the given modul are exported. This includes *all*
fields of the module but no relations. 

You can include the relations as well in the export by setting the
`--include-relations`. However this does not really include the related items
and its values but only add another field in the export with the name of the
relation in the modul. The value will be the string representation of the
related item.

You can restrict the exported items by setting a `--filter` option. With a
filter only items of the given modul matching the filter expression are
exported. The filter expression is defined in the following syntax::

        --filter search,field,isregex;[search,fieldname,isregex;...]

`search` defines the search expression and may be a regular expression if
`isregexa` is "1" else "0". `fieldname` defines the name of the field on which the
filter will apply. If field is empty, an item is exported if the search
expression matches any of the fields of the default overview configuration.

.. note::

        Filtering is limited to fields which are confiured in the items
        :ref:`overview_config`. You can not filter on fields which are not
        included in the overview. As a workaround you can setup hidden field
        in the overview config.

It is possible to define more than one filter. All filters must match to
include the item in the export.

A More detailed configurations of the export can be done by providing a
configuration file by setting the `--export-configuration` option. When using the
configuration file all other options like (format, fields or
include-relations) have no effect anymore. The default export format will be a
nested JSON which will include all configured fields.

Details on the format of the export configuration file can be found in
:ref:`exportconfiguration`.


.. _exportconfiguration:

.. autoclass:: ringo.lib.imexport.ExportConfiguration

.. index::
   single: Import
.. _clidb-import:

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

Fixing Sequences
----------------
After loading data into the database it is often needed to fix the sequences
in the database to make the incremental counters work correct::

        ringo-admin db fixsequence

ringo-admin user
================
Use the following command to get general help on the available commands::

        ringo-admin user help

Set password
------------
The password of a given user can be changed/set by invoking the following
command::

        ringo-admin user <login> --password <password>

The `password` parameter is optional. If not given ringo will autoegenerate a
new password for you.

ringo-admin fixtures
====================
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


.. _climod:

ringo-admin modul
=================
Use the following command to get general help on the available commands::

        ringo-admin modules help

Add new modul
-------------
By invoking the following command::

        ringo-admin modul add <modulname in singular form> 

A new modul will be added to your application. See :ref:`modules` for more
details.

Generate model fields from form config
--------------------------------------
By invoking the following command::

        ringo-admin modul fields <name of the modul>

The python code with the SQLAlchemy model will be generated. The code can be
pasted into the model.

ringo-admin app
===============

.. todo:: Write me.

