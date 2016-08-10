
.. _extensions:

**********
Extensions
**********

.. automodule:: ringo.lib.extension

A list of available extensions can be found on `Github
<https://github.com/ringo-framework>`_. Repositiries named `ringo_*` are
extensions.

Add an extension in your application
====================================

Adding a extension into your application, and making it available for later
coding basically consists of two basic steps:

1. Register the extension in the application. This first
   registration may include modifications of your datamodel.

2. In case of changes in the datamodel, these changes must be made
   reproducable for later installations. This is done by writing a migration
   script.


Register the extension
----------------------
First create a backup of your current database! Registering a extension in
your application may involve modifications of the database. Having a backup is
a good idea anyway but also in important step to be able to see changes made
while registering and to :ref:`extension_create_migration`.

The example assumes using a PostgreSQL database.

Here we go. First backup your database and ensure you acually have the data in
form of `INSERT` statements::

    pg_dump -a --column-inserts efa | grep INSERT > efa.dump.pre

Now register your extension in your application. Registering is done in three
steps.

In the model/__init__.py file of your application::

        import os
        from ringo.model import Base, extensions
        from ringo.lib import helpers
        
        extensions.append("ringo_news")
        
        # Dynamically import all model files here to have the model available in
        # the sqlalchemy metadata. This is needed for the schema migration with
        # alembic. Otherwise the migration will produce many table drops as the
        # tables of the models are not present in the metadata

In case your extention provides custom templates you need to configure an
additional search path for your templates in the ini file::

        # mako template settings
        mako.directories = ringo:templates
        mako.directories = ringo_evaluation:templates

Now start your application. You will notice a warning on the startup saying
that you are missing a modul entry for the new registered application::

        2016-01-15 08:49:06,652 WARNI [ringo.lib.extension][MainThread]
        Extension 'news' is missing a entry in DB. Missing migration?

For now we will initially create these entries in the database by invoking the
following command::

        ringo-admin app add-extension ringo_news

This command will add the initial entries for the extension in your database.
It time find out what actually has been added to the database to be able to
readd these modification later in the migration script::

        pg_dump -a --column-inserts efa | grep INSERT > efa.dump.post
        diff efa.dump.pre efa.dump.post | grep INSERT | sed -e 's/> //g' > inserts.sql

The file `inserts.sql` include the modification in your database to register
the extension.

The next startup of your application will show that the extension has been
loaded::

        2016-01-15 08:59:06,639 INFO  [ringo.lib.extension][MainThread]
        Extension 'news' OK

Registration is finished with this step. You now must create a migration
script to add futher tables in your database and to make the registration of
the modul persistent.

.. _extension_create_migration:

Create an initial migration script
----------------------------------
A migration script is used to make the registration and modification of the
database by the extension persistent. So you can install the application later
without doing these steps over and over again.

Lets begin with creating a new migration script by invoking the following
command::command::

        efa-admin db revision

This creates a migration script and in case the extension adds new tables to
your application the migration also include migration to add these tables.

Now add the dumped SQL statements from the `inserts.sql` into the new
generated migration script to make the registration of the new extension
happen completly in the migration script and new application can be setup in
one single step.


What next?
----------
After you registered the extension and make the changes persistent in a
migration script its time to use the extensions functionallity.

How to use the extension is heavily depended on its type. Please refer to the
extensions documention for further information. But here is a general hint:

Many extension allow to enhance the functionallity of your existing modules by
using Mixins. In case of the `ringo_tags` extension you can make modules
tagable by inheriting the `Tabable` Mixin class::

        class MyClass(Tagable, ..., BaseItem, Base):

Often these mixins require further database migration to add relations to your
model. You will need to create seperate migration scripts again by using the
`ringo-admin db revision` command.


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
