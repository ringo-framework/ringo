*******
Modules
*******

Create a new modul to your application
======================================
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
 2. Add new fields (entities) to the form. See `formbar documentation <http://formbar.readthedocs.org/>`_ for more information on how to add new entities.

 .. hint::

    If you not only add entities but also design the form, you can see the
    result immediately by reloading the create, read or update page of the
    module, depending on which form you configure. This allows you a very nice
    workflow when it comes to filling your new module with life :) Note, that
    saving data will work only if you complete all the following steps.

 3. Generate the python code to be placed in the model file by calling::

        ringo-admin model fields <modulname>

   Note that the modulname will have a "s" appended. So a modul called
   "client" becomes "clients" here. The generated code will include all
   entities defined in the form, so you will need to filter out the new fields
   on your own.

 4. Place the generated code snippet in the modul file of the modul under `model/<modulname>.py`.
 5. Generate a new revision file::

        almebic revision --autogenerate -m "Your message here"

 .. important::
    Before migrating the database please make sure you have a backup of your
    database.

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

.. important::
   This expample is outdated. The news modul has been removed from the ringo
   core and is now an external extension. Anyway see it as an example for how
   to do this in general.

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

Extending existing ringo modules
================================
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
Now we can use alembic to add the new added fields to the database. Therefor
we generate a migration script with the following command::

        app-config db revision

A new migration script should now be generated including the new added fields.
Before adding the new fields to the database please backup your old database.
Then the new fields can be added with the following command::

        app-config db upgrade

The form and table configuration can be simply overwritten by placing the form
and table config file with the same name in your application.

Finally we must tell the application to use the new created profile. The
information where to find the model clazz of the modul is stored in the
database in the field "clazzpath" for each modul.
This field can't be changed in the UI. You must to the change on the database
directly. By changing this value to the path of your new modul the application
will now use the new model. Please note, that you my need to overwrite
existing relations to be able to refer to the overwritten model.


Adding new actions to a module
==============================
Write me
