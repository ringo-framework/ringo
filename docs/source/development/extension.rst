**********
Extensions
**********

Add an extension in your application
====================================
You can add an extension with your application by registering it. Registering
is done in three steps.

In the model/__init__.py file of your application::

    import os
    from ringo.model import Base, extensions
    from ringo.lib import helpers
    
    extensions.append("ringo_evaluation")
    
    # Dynamically import all model files here to have the model available in
    # the sqlalchemy metadata. This is needed for the schema migration with
    # alembic. Otherwise the migration will produce many table drops as the
    # tables of the models are not present in the metadata

In case your extention provides custom templates you need to configure an
additional search path for your templates in the ini file::

       # mako template settings
       mako.directories = ringo:templates
       mako.directories = ringo_evaluation:templates

On the next start of your application the extension will be registerd with
your application and a new modul entry in the modules table of your application will be created.

If the extension extends the model of the application you will need to
generate a new migration script to migrate the data model and finally migrate
the model::

        alembic revision --autogenerate
        yourapp-admin db upgrade

If the extension provides a Mixin to enhance your modules functionality then
you will need to inherit from the mixin::

        class MyClass(Evaluable, Blobform, ..., BaseItem, Base):

This step can require an additional migration of your model. Please repeat the
steps to create a new migration step described before.

Create a new extension
======================
The following commands will create a new extension namend "evaluation" and
install it in your system to make it available for other applications::

    pcreate -t ringo_extension evaluation
    cd evaluation 
    python setup.py develop

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
