.. _development:

###########
Development
###########
This part describes some aspects on the ringo development. It shows how to
setup an enviroment for development, gives examples and recipes on
customisation of a ringo based application and finally shows how to test the
ringo framework.

***********************
Application development
***********************
The general layout of an development environment looks like this::

        / appname
        |-lib
        | |-ringo
        | |-formbar
        |-src
        \-env

 * appname: Root folder of the environment. Usually named with the name of the
   application.
 * lib: Folder for libraries. To be able to have differen versions of the core
   libraries ringo and formbar I recommend to install the development version
   for each application.
 * src: The source folder of your application.
 * env: The virtual python environment.

.. _development_env:

Create development environment
==============================
This section will give you an example how create a development environment.

The example shows my personal way of organising the code which was quite
handy over the last time.

First I recommend to setup a dedicated development environment based on a
`Virtual Python Environment <https://pypi.python.org/pypi/virtualenv>`_ for
each application (including ringo itself) you want to develop::


        cd /path/to/your/development/root/folder
        # create a folder for the application you like to create.
        mkdir <yourappname>
        cd <yourappname>

        # Create and activate a new virtual environment and do all following
        steps with # the activaed virtual env.
        virtualenv --no-site-packages env
        source env/bin/activate

        # create a subfolder for all libs external libs.
        mkdir lib
        cd lib
        # Install a development version of brabbel
        hg clone https://bitbucket.org/ti/brabbel
        cd formbar
        # Install a development version of formbar.
        hg clone https://bitbucket.org/ti/formbar
        cd formbar
        python setup.py develop
        # Install a development version of ringo.
        hg clone https://bitbucket.org/ti/ringo
        cd ringo
        python setup.py develop
        cd ..

We are almost finished. The next step is either to create a new application
with this environment or get an existing application.

.. _create_ringo_based_application:

Working on an existing application
----------------------------------
Simply clone the exiting application::

        # Change to your development folder
        cd <yourappname>
        # Get the application
        hg clone https://bitbucket/ti/plorma
        # Rename the folder to meet the naming convention
        mv plorma src
        cd src
        python setup.py develop


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



*****
Tests
*****
Ringo come two types of tests:

 1. Functional and Unit tests and
 2. Behaviour driven tests using the `Behave <http://www.behave.org>`_ framework. All tests are located are under "ringo/tests" directory.

Start the tests by invoking the following command::

        invoke tests

This will create new test database calls the tests and make some statistics on
the code coverage.

***********
Translation
***********
Translation of ringo is managed using `the Transifex webservice <https://www.transifex.com/projects/p/ringo/>`_
