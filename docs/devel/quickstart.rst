**********
Quickstart
**********

.. _minimalapp:

A minimal Application
=====================

Activate the virtualenv and change into you development environment::

        cd /path/to/your/development/environment
        source env/bin/activate

Create a fresh application based on a ringo project template::

        pcreate -t ringo foo
        mv foo src
        cd src
        python setup.py develop

Optional: Setup the database connection in the generated *development.ini*
file and configure the user you created in the process of installing
:ref:`installpostgresql`. If you followed the instructions you're done and no
further action is needed. However here is an example how to change the
connection to database.::

        -sqlalchemy.url = postgresql://@/foo
        +sqlalchemy.url = postgresql://user:password@localhost/foo 

Create a new database for your application and initialise the database using
the :ref:`clidb`::

        createdb foo
        foo-admin db init

Start the application::

        pserve --reload development.ini

Extending existing Application
==============================
Ringo allows to build applications which are based on another application.
I will call it `baseapp` from now on.
This needs some further steps after you created a single application as
described in :ref:`minimalapp`.

You need to add the baseapp into your requirements file.

After creating the application you need to modify the `__init__.py` file of
your application to include the configuration of the baseapp application::

        # Include basic ringo configuration.
        config.include('ringo')
        config.include('baseapp')
        config.include('yourapp')
        for extension in extensions:
            config.include(extension)
        ...
        config.scan('baseapp')
        config.scan()
        
If you also have overwritten views in your baseapp application you must also 
scan the foo package. Otherwide you application is not aware of these overwritten 

In your `ini` file you need to set the base of your new application::

        app.base = baseapp

In your `ini` file you need to add the directories for the mako templates::

        # mako template settings
        mako.directories =
            yourapp:templates
            baseapp:templates
            ringo:templates
        mako.default_filters = h

`baseapp` is the name of the application which you want to use as a base.
`yourapp` is the name of the application you are creating.

In order to have a working migration setup you will need to import the
model of the base appliction to the model of the inherited application::

       import bar.model

This will ensure that all the model will be available to alembic. Otherwise
many tables would be scheduled for a drop.

The initialisation of the database is a little bit different as we want to
initialize the database with the migration scripts and fixtures of baseapp::

        bar-admin db init --base baseapp
        bar-admin fixtures load --app baseapp

While the migration scripts are copied from baseapp to yourap when initialising the
database for the first time, the fixtures are not! yourapp only
includes the fixtures from the base ringo application. If you want to use the
fixtures from baseapp on default, then you need to copy the files yourself::

        rm </path/to/yourapp/yourapp/fixtures/*
        cp -r <path/to/baseapp/baseapp/fixtures/* </path/to/yourapp/yourapp/fixtures


Voilà! That is it.

