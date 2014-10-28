
.. _development:

###########
Development
###########
This part describes some aspects on the ringo development. It shows how to
setup an enviroment for development, gives examples and recipes on
customisation of a ringo based application and finally shows how to test the
ringo framework.

Ringo is not just a library which can be used in other applications.
Ringo is also standalone application! This means you can start Ringo
and click around in the web application and use all the features provided by
Ringo.

This is very helpful when developing features in ringo, as you can see
immediately the result of your changes without effects from applications based
on ringo.

.. _development_env:

Environment
***********
This chapter will show you how to build a development environment for ringo
development. The example shows my personal way of organising the code which was quite
handy over the last time.

First I recommend to setup a dedicated development environment based on a
`Virtual Python Environment <https://pypi.python.org/pypi/virtualenv>`_ for
each application (including ringo itself) you want to develop.

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

Setup
=====
This section will give you an example how create a development environment for
an existing ringo based application named `Plorma <https://bitbucket.org/ti/plorma>`_::

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
        # Install a development version of formbar.
        hg clone https://bitbucket.org/ti/formbar
        cd formbar
        python setup.py develop
        # Install a development version of ringo.
        hg clone https://bitbucket.org/ti/ringo
        cd ringo
        python setup.py develop
        cd ..

        # Checkout the application you want to work on.
        hg clone https://bitbucket.org/ti/plorma src
        cd src
        python setup.py develop

That is all. The environment is now ready. Follow the steps described in the
README comming with the source of the application to initialize and start the
application.

.. _create_ringo_based_application:


General
*******

Core development
================
Core development means working on the ringo framework itself. The environment
descibed in :ref:`development_env` can be used too. Just work in the
`lib` folder.

Ringo is not just a library which can be used in other applications.
Ringo is also standalone application! This means you can start Ringo
and click around in the web application and use all the features provided by
Ringo.

This is very helpful when developing features in ringo, as you can see
immediately the result of your changes without effects from applications based
on ringo.

See the README file coming with ringo to see how to initialize and setup a
standalone version of ringo.

App development
===============
The setup process in :ref:`development_env` already describes how to setup an
enviroment for an existing ringo based application.

If you want to start to work on a new ringo application head over to the next
section.


Create a new application
------------------------
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


Customisation / Recipes
***********************
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

Add a new extension
===================
The following commands will create a new extension namend "evaluation" and
install it in your system to make it available for other applications::

    pcreate -t ringo_extension evaluation
    cd evaluation 
    python setup.py develop

Now can can register the new extension for the first time with your
application. Registering is done in three steps.

In the model/__init__.py file of your application::

    import os
    from ringo.model import Base, extensions
    from ringo.lib import helpers
    
    extensions.append("ringo_evaluation")
    
    # Dynamically import all model files here to have the model available in
    # the sqlalchemy metadata. This is needed for the schema migration with
    # alembic. Otherwise the migration will produce many table drops as the
    # tables of the models are not present in the metadata

If your extension provides some extension specific actions they should be
implemented in a Extension Mixin class. Overwrite the 'get_mixin_actions'
method to define the actions the extension should provide to other modules::

        class Evaluable(Mixin):

            @classmethod
            def get_mixin_actions(cls):
                actions = []
                # Add Evaluation action
                action = ActionItem()
                action.name = 'Evaluate'
                action.url = 'evaluate/{id}'
                action.icon = 'glyphicon glyphicon-stats'
                action.permission = 'read'
                action.bundle = True
                actions.append(action)
                return actions

To make the actions available in other modules you need to Inherit form this
mixin::

        class MyClass(Evaluable, Blobform, ..., BaseItem, Base):

In case your extention provides custom templates you need to configure an
additional search path for your templates in the ini file::

       # mako template settings
       mako.directories = ringo:templates
       mako.directories = ringo_evaluation:templates

On the next start of your application the extension will be registerd with
your application and a new modul entry will be created.

.. _add_modules:

Add a new modul to your application
===================================
If you want to add a new modul to your ringo based application or the the
ringo base then you should use the ringo-admin command::

        ringo-admin modul add name
        ringo-admin db upgrade

The the help page of the command for more informations.

The generated modul only has some default fields like the `uuid` or `id`
field. In the next step you can extend the new modul with fields. See
:ref:`_add_fields` for more information.


.. _add_fields:

Adding new fields to the model
==============================
Adding new fields to the model of a modul can be achieved by the following
steps.

 1. First open the form definiton which is located under `views/forms/<modulname>.xml`. 
 2. Add new fields (entities) to the form. See `formbar documentation <http://pythonhosted.org//formbar/>`_ for more information on how to add new entities.
 3. Generate the python code to be placed in the model file by calling::

        ringo-admin model fields <modulname>

   Note that the modulname will have a "s" appended. So a modul called
   "client" becomes "clients" here. The generated code will include all
   entities defined in the form, so you will need to filter out the new fields
   on your own.

 4. Place the generated code snippet in the modul file of the modul under `model/<modulname>.py`.
 5. Generate a new revision file::

        almebic revision --autogenerate -m "Your message here"

 6. Migrate database::

        ringo-admin db upgrade

 7. Commit the changes.


.. _add_action:

Adding a single custom actions to a module
==========================================
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
==============================
Write me

Overwriting static files
========================

Configuring forms
=================
Simply overwrite the form configuration in your application

Configuring overviews
=====================
Simply overwrite the table configuration in your application

Extending existing ringo models
===============================
Ringo comes with some predefined modules which provide some common
functionality. However the modules might not match your need, so they can be
extended or modified.

Add new fields to the model
---------------------------
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
----------------------------------------
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
---------------------------------------------
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
=========================
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
============================
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
==================================
The name of the application is defined in the "ini" file. Check the
``app.title`` configuration variable.

Tests
*****
Ringo come two types of tests:

 1. Functional and Unit tests and
 2. Behaviour driven tests using the `Behave <http://www.behave.org>`_ framework. All tests are located are under "ringo/tests" directory.

Start the tests by invoking the following command::

        invoke tests

This will create new test database calls the tests and make some statistics on
the code coverage.

Translation
***********
Translation of ringo is managed using `the Transifex webservice <https://www.transifex.com/projects/p/plorma/>`_
