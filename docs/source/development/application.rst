***********
Application
***********


Create a new application
========================
Creating a new Ringo based application is easy. In the following example we
will create an new application named ''yourappname''. As precodition a
development environment must be already created (expect the application
specific part) and the virtual environment is activated. The new application
can be created with the following commands::

        # Change to your development folder
        cd <yourappname>
        # Create the new application
        pcreate -s ringo <yourappname>
        # Rename the folder to meet the naming convention
        mv <yourappname> src
        cd src
        python setup.py develop

This will trigger the creation of an application skeleton based on the
:ref:`scaffold_basic`.

Create a new application based on another application
-----------------------------------------------------
Lets say you have a appliation called ''Foo'' which should be used as a
platform in the same way as ringo was a platform for the ''Foo'' application.
Now you want to create an application ''Bar'' based on ''Foo''.

The procedure to this is almost the same despite three things.

1. After creating the application you need to modify the `__init__.py` file of
your application to include the configuration of the ''Foo'' application::

        # Include basic ringo configuration.
        config.include('ringo')
        config.include('foo')
        config.include('bar')
        for extension in extensions:
            config.include(extension)
        ...
        config.scan('foo')
        config.scan()
        
If you also have overwritten views in your ''Foo'' application you must also 
scan the foo package. Otherwide you application is not aware of these overwritten 
methods.

2. The search path for the mako templates need to be extended as we want the
templates of the ''Foo'' application in our application too::

        # mako template settings
        mako.directories =
                bar:templates
                foo:templates
                ringo:templates

3. In order to have a working migration setup you will need to import the
model of the base appliction to the model of the inherited application::

       import bar.Model

This will ensure that all the model will be available to alembic. Otherwise
many tables would be scheduled for a drop.

4. The initialisation of the database is a little bit different as we want to
initialize the database with the migration scripts of ''Foo''::
        
        bar-admin db init --base foo
        bar-admin fixtures load --app foo

Voilà! That is it.

Ringo core development
======================
Core development means working on the ringo framework itself.

Ringo is not just a library which can be used in other applications.
Ringo is also standalone application! This means you can start Ringo
and click around in the web application and use all the features provided by
Ringo.

This is very helpful when developing features in ringo, as you can see
immediately the result of your changes without effects from applications based
on ringo.

The because ringo is also a standalone application, the core development is a
special case of the application development.
