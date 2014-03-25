
.. _development:

***********
Development
***********

.. _installation_development:

Setup a developmet environment
==============================
If you plan to do any development with Ringo I recommend to setup a dedicated
development environment based on a `Virtual Python Environment
<https://pypi.python.org/pypi/virtualenv>`_.

This section will give you an example how create a development environment if
you want to work on Ringo itself or if you want to create a Ringo based application.

First create a new folder where all the development will happen. Then create a
new Virtual Python Environment::

        cd /path/to/your/development/folder
        # create a folder where all the ringo development happens.
        mkdir ringo
        # create a subfolder where all the application development happens.
        mkdir applications

        # setup ringo.
        cd ringo
        virtualenv --no-site-packages python
        # Activate your virtual environment and do all following steps with
        # the activaed virtual env.
        source python/bin/activate

Now setup Ringo by getting the source from Bitbucket and installing it in the
Virtual Python Environment::

        hg clone https://bitbucket.org/ti/ringo
        cd ringo
        # Do only set a link to the Ringo application if you plan to develop
        # on Ringo itself. Else you can also use "install" instead of "develop"
        python setup.py development

If you only want to work on Ringo itself you are ready here and can continue
to read the :ref:`develop_ringo_application` section.

If you want to create a new Ringo based application you should head
over to the :ref:`create_ringo_based_application` section and continue the
setup.

.. _develop_ringo_application:

Develop on Ringo
----------------
Ringo is not just a library which can be used in other applications.
Ringo is for itself a standalone application! This means you can start Ringo
and click around in the web application and use all the features provided by
Ringo.

This is very helpful as can see immediately the result of your changes.

To develop on Ringo you obviously must have installed Ringo.
This is explained in the :ref:`installation_development` section.
After you installed Ringo for development the last final steps is to
initialize the application. Please follow the instruction documented in the
README file coming with Ringo::

        # Change to your development folder
        cd /path/to/your/development/folder/ringo/
        cd ringo
        cat README.rst

That is it. You are ready to go!

.. _create_ringo_based_application:

Develop/Create on a Ringo based application
-------------------------------------------
To create a Ringo based application you obviously must have installed Ringo.
The can be done either explained in the :ref:`installation_production` or :ref:`installation_development` section.

You can now create a new Ringo based application. In the following example we
will create an new application named ''MyFirstRingoApp''::

        # Change to your development folder
        cd /path/to/your/development/folder/ringo/applications
        # Create a subfolder Change to your development folder
        cd applications
        pcreate -s ringo MyFirstRingoApp

This will trigger the creation of an application skeleton based on the
:ref:`scaffold_basic`.

Now you can initialize and start your fresh created application by following
the instructions provided in the README file with the application folder::

        cd MyFirstRingoApp
        cat README.rst

Your application is ready for development :)

.. _add_modules:

Add a new modul to your application
===================================
If you want to add a new modul to your ringo based application or the the
ringo base then you should follow the steps described below.

 1. Call the :ref:commands_add_modul_ add_modul command to add the new modul.

.. important::

        Make sure your application codebase is up to date. This includes the
        application code, ringo and the database. Are all changes commited?

This was easy, ey?
But this is only the quick shot. For more advanced usage proceed to the next
section.

.. _alembic_migration:

Using alembic for database migration
------------------------------------
In order to be able to migrate your database also, the precedure of creating a
new modul gets a little bit more complex::

        # 1. Backup your database to be able to generate the new added INSERTS
        # statements.
        cp myproject.sqlite myproject.sqlite.orig
        sqlite3 myproject.sqlite.orig .dump | grep INSERT > inserts.orig

        # 2. Call the :ref:commands_add_modul_ add_modul command to add the
        # new modul.
        add_myproject_modul mymodul --config=development.ini

        # 3. Generate new new added INSERTS statements.
        sqlite3 myproject.sqlite .dump | grep INSERT > inserts.modified
        diff -n inserts.orig inserts.modified | grep INSERT > inserts.new

        # 4. Now revert the database and generate a migration file.
        cp myproject.sqlite.orig myproject.sqlite
        alembic revision --autogenerate

        # 5. Add the statements from inserts.new into the genrated migration
        # file. If you need any modifications, make sure you also modificate the
        # init_modul method in the model file of the new added modul.

        # 6. Finally remove temporary files
        rm myproject.sqlite.orig
        rm inserts.orig
        rm inserts.modified
        rm inserts.new

After these steps you should be able to migrate your application by using
your SCM to versionize the application code base and by using alembic your
the database versioning.

Customisation
=============
The behaviour of the application can be modified in different ways. You can
customize the

 * *View*: Change visual aspects like the layout of forms, overviews and or the whole page layout.
 * *Model*: Add attributes or methods to your model.
 * *Logic*: Custimize the application logic located in the application view.

So nearly all aspects can be changed more or less easily.

First you need to know what you are about to change. Is it something which is defined in the
ringo base application, or is it in your own application? This is important as
it determines the method to apply to change the behaviour.

If you want to change to behaviour of your own application the things to do
should be quite clear: Do the changes directly in the relevant templates,
model or views.

If you want to change the behaviour defined in the ringo app you have
different options. Static files are usually overwritten. Models are extended
or modified by overwriting or extending a inherited version of the ringo model
in your application. The application logic can be modified be relinking the
mapped functions on URLs.

In the next sections I will give some examples on how to customise things in a
ringo application.

.. _add_action:

Adding a single custom actions to a module
------------------------------------------
If you are need specific single action to your modul you need to do the following steps. 

.. note::
   Adding such an actions is only loose integrated into the ringo framework.
   So will not be able to configure the permission in the webinterface and the
   actions will not be listed automatically anywhere in the application.

I will explain it with the example of adding a "Mark as read" operation for
the news modul. This is a very specific actions which is only used in the
newslisting. Adding such a specific action as new generic action for the modul
as described in :ref:`newmodulaction` would be overkill.

 1. Configure the routes and views
 2. Implement action in view.

First configure the route for the new action. Open the __init__ file of your
application and search for the section where the routing is configured. There
insert the following line::

    config.add_route(News.get_action_routename(News, 'markasread', prefix='rest'),
                     'rest/news/{id}/markasread',
                     factory=get_resource_factory(News))

Now implement the new action in the view. Open 'views/news.py' and add the
following code::

        @view_config(route_name=News.get_action_routename(News, 'markasread', prefix='rest'),
                        renderer='json',
                        request_method="PATCH",
                        permission='read')
        def rest_markasread(request):
            ... your code


.. _newmodulactions:

Adding new actions to a module
------------------------------
Write me

Overwriting static files
------------------------

Configuring forms
-----------------
Simply overwrite the form configuration in your application

Configuring overviews
---------------------
Simply overwrite the table configuration in your application

Extending existing ringo models
-------------------------------
Ringo comes with some predefined modules which provide some common
functionality. However the modules might not match your need, so they can be
extended or modified.

Add new fields to the model
^^^^^^^^^^^^^^^^^^^^^^^^^^^
You need to create a new model file in your application. In this file
create a model which inherits from the base modul and add attributes and
extend or overwrite functions as needed. In the following example we add two
additional columns to the base Profile modul::

        import sqlalchemy as sa
        from ringo.model.user import Profile

        class MyProfile(Profile):
        """Specific profile. Inherited from ringos base profile"""
            col1 = sa.Column(sa.Text)
            col2 = sa.Column(sa.Text)
            ...

            # Overwrite relation with a new backref name to be able to refer
            # to the new Profile in the user object. Will raise a SAWarning.
            user = sa.orm.relation("User", cascade="all, delete-orphan",
                                   backref="pprofile", single_parent=True,
                                   uselist=False)

            def __unicode__(self):
                return "%s" % (self.col1)

Overwrite existing Statemachine/Workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you want to change the statemachine/workflow for the model you need
overwrite some attributes of the modul in order to inject your new
StateMachine.  In the follwing example we overwrite the StateMachine of the
imaginary class "Foo" which has a statemachine available under the name
"foo_state".::

        import sqlalchemy as sa
        from ringo.model.statemachine import Statemachine, State, \
        null_handler as handler, null_condition as condition
        import Bar

        class FooStatemachine(Statemachine):

            def setup(self):
                # Do the setup here

        class Foo(Bar):
            # Overwrite attributes of the StateMixin from the inherited
            # clazz to inject the custom statemachine.
            _statemachines = {'foo_state_id': FooStatemachine}

            @property
            def foo_state(self):
                state = self.get_statemachine('foo_state_id')
                return state.get_state()

Let your application know about the new model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Next we need to import the new model in the __init__.py file of the application::

        from myapp.model.modul import Modul
        # AUTOREPLACEIMPORT
        # END AUTOGENERATED IMPORTS
        from myapp.model.profile import MyProfile

Now we can use alembic to add the new added fields to the database. Therefor
we generate a migration script with the following command::

        alembic revision --autogenerate -m "Added new fields to the Profile modul"

A new migration script should now be generated including the new added fields.
Before adding the new fields to the database please backup your old database.
Then the new fields can be added with the following command::

        alembic upgrade head

The form and table configuration can be simply overwritten by placing the form
and table config file with the same name in your application.

Finally we must tell the application to use the new created profile. The
information where to find the model clazz of the modul is stored in the
database in the field "clazzpath" for each modul.
This field can't be changed in the UI. You must to the change on the database
directly. By changing this value to the path of your new modul the application
will now use the new model. Please note, that you my need to overwrite
existing relations to be able to refer to the overwritten model.

Calling alternative views
-------------------------
Application logic is defined in the view function. The view for the model was
setup on initialisation of the application and uses the default view logic in
ringo by default.
But the view for specific actions can be overwritten.
In the following example we will overwrite the default 'index' method of the
'home' view. So you need to define your custom method in your view file view
file::

        @view_config(route_name='home', renderer='/index.mako')
        def index_view(request):
            # Write your own logic here.
            handle_history(request)
            values = {}
            ...
            return values

Note, that we reconfigure the view by calling 'view_config' with an already
configured route_name. This will overwrite the configured view and the
application will use your custom view now for the route named 'home'.

If you only want to extend the functionallity from the default you can do this
too. No need to rewrite the default logic again in your custom view::

        from ringo.views.home import index_view as ringo_index_view

        @view_config(route_name='home', renderer='/index.mako')
        def index_view(request):
            # First call the default view.
            values = ringo_index_view(request)
            # Now extend the logic.
            ...
            # Finally return the values.
            return values

Using callbacks in the views
----------------------------
Callback kann be used to implement custom application logic after the logic of
the default view has been processed. This is usefull e.g if you want to send
notification mails, modifiy values after a new item has been created or clean
up things after something has been deleted.

A callback has the following structure::

        def foo_callback(request, item):
            """
            :request: Current request
            :item: Item which has been created, edited, deleted...
            :returns item
            """
            # Do something with the item and finally return the item.
            return item

The reqeust an item should give you all the context you should need to to the
desired modifications.

The callback must be supplied in the call of the main view function like
this::

        @view_config(route_name=Foo.get_action_routename('create'),
                renderer='/default/create.mako',
                permission='create')
        def create(request):
                return create_(Foo, request, callback=foo_callback)

Change the name of the application
----------------------------------
The name of the application is defined in the "ini" file. Check the
``app.title`` configuration variable.

Tests
=====
Ringo come two types of tests:

 1. Functional and Unit tests and
 2. Behaviour driven tests using the `Behave <http://www.behave.org>`_ framework. All tests are located are under "ringo/tests" directory.

Functional and Unit tests
-------------------------
.. warning::
   These tests are outdated and must be fixed. Most of the functionality is
   now implemented in the behave tests.

Start the tests by invoking the following command::

        initialize_ringo_db test.ini
        python setup.py test

        # or if you want some codemetrics using coverage
        nosetests

        # Finally delete the test database
        rm test.sqlite

Behave
------
Behave is nice! You will like it too :) Go and read the documentation.

Tests can be triggered by invoking the following command::

        sh test.sh

This will create new test database calls the tests and make some statistics on
the code coverage.
