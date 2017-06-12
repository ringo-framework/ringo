******************
Tutorials / Howtos
******************


.. _import_export:
.. index::
   single: Export
   single: Import

Importing and Exporting data
============================
It is possible to export and import the data of modules in different formats.
Supported formats are **JSON** and **CSV**. The default is to export and
import JSON.

Export can be triggered in the UI (If the user has sufficient permissions, and
export is enabled) or using the CLI commands from :ref:`clidb` to
:ref:`clidb-export` and :ref:`clidb-import`.

How to make config changes permanent
====================================
Ringo allows to change the configuration of the application through the UI in
many ways. You can add new roles, set permissions etc. All those changes are
done in the database.
As those changes will get lost when dropping and recreating the database we
need a way to make save these changes in a way that they do not get lost when
reinitialize the application.

The typical way is to write a migration script and to put the changes you made
into this script. An empty migration script can be generated like this::

        ringo-admin db revision

An easy way to get the changes in the database is to diff between the dump of
the database. On dump is done before the changes are mare::

        DB=ringo
        pg_dump -a --column-inserts $DB | grep INSERT > $DB.dump.pre

Now you can do the changes in the application and dump the database again::

        pg_dump -a --column-inserts $DB | grep INSERT > $DB.dump.post

Finally you diff the two dumps and ideally get the changes made in the
database ready to put into the migration script::

        diff $DB.dump.pre $DB.dump.post | grep INSERT | sed -e 's/> //g' > inserts.sql



Work with modules
=================

.. _add_modul:

Add a new modul
---------------

Please make sure you understand the concept of :ref:`modules` before adding a
new module. In some cases it might be sufficient to only :ref:`add_view`.

First you create the initial files and a migration to "install" the module in
your application using the :ref:`climod` command. Please use the singular form
of the name of the module::

        ringo-admin modul add <modulname in singular form>

This will generate a bunch of files:

 * A model file
 * A XML configuration for the form configuration
 * A JSON configuration for the overview/listing configuration
 * A migration file to install the modul.

Upgrade the database to apply the generated migration and to install the
initial data for the module by using the :ref:`clidb` command::

        ringo-admin db upgrade

The module is now installed and ready for use. Restart your application. The
module should now be listed in the main menu. You can already call all CRUD
actions of the module, but for now no data is saved as the model of the module
is basically empty. So its time to add some fields to your new module.


Add new fields
--------------
Adding new fields to the module means finally means adding new fields to the
model of the module and finally to do a migration.

There are two ways to to this:

 1. You do all the work on your own and add the fields directly in the model file of your module. If you want to choose this way I recommend reading the `SQLAlchemy documentation on Decalaritve Mapping <http://docs.sqlalchemy.org/en/latest/orm/mapping_styles.html#declarative-mapping>`_

 2. You focus on developing the form of the module and let Ringo generate the relevant part of the model your you. This way you only need to copy and paste the generated model code into your model. If you choose this way than you should become familiar with the :ref:`formconfig` (Which is a crucial part of Ringo development anyway).

Whatever way you choose it finally ends in the generating a migration file
and upgrading the database using the :ref:`clidb` command::

        ringo-admin db revision
        ringo-admin db upgrade

Build relations between modules
-------------------------------
Adding a relation between two modules is usually done in two steps:

 1. Add fields to the model for the foreign key and add an ORM relation.
 2. Migrate the database.

Here is a short example from `ringo/model/user.py`::

        class User(BaseItem, Owned, Base):
                ...
                sid = sa.Column(sa.Integer, sa.ForeignKey('user_settings.id'))
                # user_settings is the name of the table in the database for
                # the settings. This field refers to the id column of that
                # table.
                ...
                settings = sa.orm.relationship("UserSetting", uselist=False,
                                               cascade="all,delete")
                # UserSetting is the name of the Python class to which the
                relation is set.

If you want to use this relation later in forms than you must refer to the
`settings` attribute of the User and **not** to foreign key.

There is nothing specific in Ringo on adding a foreign key and a relation to
the model so all relevant information can be found in the `ORM
documentation <http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html>`_ of SQLAlchemy.

.. tip::
        If you have a bidirectional relation between to modules we recommend
        to set up the ORM relation in both modules instead of using the
        *backlink* feature of SQLAlchemy. Writing to relations tends to be
        better readable esspecially when it comes to cascading rules.

.. _add_mixin:

Extend modul with a mixin
-------------------------
Please make sure you understand the concept of :ref:`mixins` before extending the module. In some cases it might be sufficient to only :ref:`add_view` or :ref:`add_action`.


.. index::
   single: CRUD
   single: Action
   single: Bundle
   single: Bundled Action

.. _add_action:

Add a new action to a modul
---------------------------
Initially each module has only the default :ref:`crud` actions available.
However the module can be extended by adding a new specific action.

In the following example we will add a `foo` action to the `bar` module.

Action entry
^^^^^^^^^^^^

Get the modul id of the `bar` modul from the database::

        select id from modules where name = 'bar';
        -> 1000

Get the max id in the actions table::

        select max(id) from actions;
        -> 118

Add a new action entry for this module in the database. Create a new migration
file for this::

        ringo-admin db revision

Open the new generated migration file and add the following statement to
upgrade the database. Use the modul id
and the next id of the action entry::

        INSERT INTO actions (id, mid, name, url, icon, description, bundle, display, permission) 
        VALUES (119, 1000, 'Foo', 'foo/{id}', 'icon-eye-read', '', false, '', '');

.. note::
        If you want to add a action which should also be available as a
        bundled action (selectable from the dropdown on the overview page) you
        need to set the `bundle` attribute to 'true'.

Find details on the values for the action entry in `ActionItem source
<https://github.com/ringo-framework/ringo/blob/master/ringo/model/modul.py#L46>`_


Don't forget to add the statement to downgrade the migration as well::

        DELETE FROM actions where id = 119;

After manual inserting a new action entry in the database you need to fix the
sequences in the database::

        ringo-admin db fixsequence


View
^^^^
Create a new callable for the `foo` action. Usually this is done in the
`/views/bar.py`::

        from pyramid.view import view_config
        from ringo.lib.helpers import get_action_routename

        from myapp.model.bar import Bar 

        @view_config(route_name=get_action_routename(Bar, "foo"),
                     renderer="/foo.mako")
        def my_foo_view(request):
            # Implement logic here.
            return {}

Bundle view
^^^^^^^^^^^
This is an example of a simple bundled action::

        from ringo.lib.helpers import get_action_routename
        from ringo.views.base.list_ import set_bundle_action_handler
        from ringo.views.request import is_confirmed
        from ringo.lib.renderer import (
                ConfirmDialogRenderer,
                InfoDialogRenderer
        )

        from myapp.model.bar import Bar

        def my_bundle_view(request, items, callback=None):
            if (request.method == 'POST' and
                is_confirmed(request)):
                    for item in items:
                        pass # Do the action for each item here.
                    renderer = InfoDialogRenderer(request, "Title", "Body")
                    rvalue = {}
                    rvalue['dialog'] = renderer.render(url=request.route_path(get_action_routename(Bar, "list")))
                    return rvalue
            else:
                renderer = ConfirmDialogRenderer(request, Bar, "foo", "Title")
                rvalue = {}
                rvalue['dialog'] = renderer.render(items)
                return rvalue

        set_bundle_action_handler("foo", my_bundle_view)

This bundled action will show a confirmation dialog which needs to be
confirmed. After that the view will iterate over all selected items and show a
info dialog at the end.

Permissions
^^^^^^^^^^^
Modifications on the permissions should be done in a migration script::

        ringo-admin db revision

So here are the required steps to craft the needed INSERT and DELETE
statements.

First get the id of the role which should be able to call the action::

       SELECT id FROM roles WHERE name = 'users';
       -> 2

Now SQL statements for the migration script will be::

        INSERT INTO nm_actions_roles (aid, rid) VALUES (119, 2);
        DELETE FROM nm_actions_roles WHERE aid = 119 and rid = 2;

As always when manually inserting something in the database call the
fixsequence command::

        ringo-admin db fixsequence/gp_dump


Setup breadcrumbs
-----------------
Breadcrumbs are a great way to help users to navigate through a nested set of
related modules and alway show them where they are.

Ringo can show breadcrumbs. They are optional. If you want them you need to
configure a `Sitemap`. The sitemap is build in the *__init__.py* file of your
application::

        from ringo.lib.sitetree import site_tree_branches
        sitetree = { your sitetree configureation goes here }
        site_tree_branches.append(sitetree)

For a detailed description on how to build a see the documentation of the
sitetree module.

.. rubric:: Sitetree module

.. automodule:: ringo.lib.sitetree

Work with extensions
====================

Add a new extension
-------------------

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



Use an extension
----------------

Adding a extension into your application, and making it available for later
coding basically consists of two basic steps:

1. Register the extension in the application. This first
   registration may include modifications of your datamodel.

2. In case of changes in the datamodel, these changes must be made
   reproducable for later installations. This is done by writing a migration
   script.


.. rubric:: Register the extension

First create a backup of your current database! Registering a extension in
your application may involve modifications of the database. Having a backup is
a good idea anyway but also in important step to be able to see changes made
while registering.

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

.. rubric:: Create an initial migration script

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


.. rubric:: What next?

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


.. _formconfig:

Form configuration
==================
Form configuration is done in XML files. Configurations are stored in
`<yourproject>/views/forms/` folder.

Ringo uses the `formbar <https://formbar.readthedocs.io>`_ library
for form handling.it gives you plenty of nice features like easy design,
validation, conditional fields and rule expressions to only name some of them.

.. tip::
        You can easily add fields to the form, change the layout and see the
        results immediately when you reload the page. This is a great help
        when you design forms. The only restriction to this is storing the
        data and doing 

Please have a look into the `formbar documentation <https://formbar.readthedocs.io/en/latest/>`_ to learn how to configure forms using formbar and check the forms in `ringo/views/forms` for some examples.

Generate model fields
---------------------
After you have added new fields to the form you need to add those fields to
the model too. Ringo provides a small helper command for this which will
generate the relevant fields from the given form for your model::

        ringo-admin modul fields <name of modul in plural form>

This will print some code to *stdout* which can be pasted into the model of
the module.

Don't forget to generate migration and upgrade the database::

        ringo-admin db revision
        ringo-admin db upgrade

Ringo specific renderer
-----------------------
Ringo comes with some specific renderers which extends the default renderers
of formbar. They usually are aware of accessing to Ringo specific attributes
like permissions checks e.g.

.. index::
   triple: Form;Renderer;Checkbox

Checkbox
^^^^^^^^
.. autoclass:: ringo.lib.renderer.form.CheckboxFieldRenderer

.. index::
   triple: Form;Renderer;Dropdown

Dropdown
^^^^^^^^
.. autoclass:: ringo.lib.renderer.form.DropdownFieldRenderer

.. index::
   triple: Form;Renderer;Links

Links
^^^^^
.. autoclass:: ringo.lib.renderer.form.LinkFieldRenderer

.. index::
   triple: Form;Renderer;Listings

Listings
^^^^^^^^
.. autoclass:: ringo.lib.renderer.form.ListingFieldRenderer

State
^^^^^
.. autoclass:: ringo.lib.renderer.form.StateFieldRenderer


Writing a new renderer
----------------------
Ringo let you easily define your own custom renderer. Custom renderers are
used to display the data in a free defined form. You can define new input
elements or present you data in diagram e.g.

Writing an using custom renderers is done in two steps:

 1. You write the renderer and templates
 2. You bind in the new renderer in the application

Renderer part
^^^^^^^^^^^^^
First create a new renderer by ineriting from an existing one. Formbar and
Ringo already provide some renderers which can be used. Renderers are usally
located in `lib/renderer.py` or `lib/renderer/form.py`.

Here you see the code for a simple renderer::

        import os
        import pkg_resources
        from mako.lookup import TemplateLookup
        from formbar.renderer import FieldRenderer
        from ringo.lib.renderer.form import renderers

        # We need to configure the template lookup system and "register" a new
        # location of the templates. Mako will search in this locations for
        # templates to render.
        base_dir = pkg_resources.get_distribution("namofapplication").location
        template_dir = os.path.join(base_dir, 'nameofapplication', 'templates')
        template_lookup = TemplateLookup(directories=[template_dir],
                                         default_filters=['h'])

        # Now create your renderer. And define the template which is used on
        # rendering.
        class MyFieldRenderer(FieldRenderer):

            def __init__(self, field, translate):
                FieldRenderer.__init__(self, field, translate)
                self.template = template_lookup.get_template("path/to/field/template.mako")


        # Finally register the template in ringo to make the renderer known in
        # formbar.
        renderers['myrenderer'] = Myfieldrenderer

A template looks like this::
        
        <div id="${field.id}">
                I'm the body of your field with name ${field.name}. In
                ${field._form} which is there to render fields of
                ${field._form._item} with renderer ${field.renderer}. Add
                content here.
        </div>


View part
^^^^^^^^^
Using the new renderer is about configuring the renderer for an entity::

        <entity ...>
                <renderer type="myrenderer"/>
        </entity>

The type of the renderer is the name of the renderer under which it has been
registered in ringo.

Using forms in views
--------------------
Here is some pseudo code to get the idea. In the first step you need to get
the form::

        from ringo.views.helpers import (
                get_item_form, 
                render_item_form
        )
        from ringo.views.request import (
                handle_POST_request,
                handle_redirect_on_success
        )


        # This is currently hackish :( A form needs the class and the item.
        # This is usally part of the request already in case of the defalt CRUD
        # actions. If we have a custom view we need to set those attributes in
        # the request for ourself.
        request.context.__model__ = ItemClass 
        request.context.item = item

        form = get_item_form('nameoftheform', request)

Now we need to handle POST request of the form in case we actually want to
save data and not only render the form. We use standard Ringo functionality
for this::

        if request.POST:
                if handle_POST_request(form, request):
                        url = request.route_patch("nameofthisroute")
                        return handle_redirect_on_success(request, backurl=url)

        # In all other cases render the form. It's now up to you to return the
        # rendererd form to the template.
        rendered_form = render_item_form(request, form)

.. _overview_config:

Overview configuration
======================

.. autoclass:: ringo.lib.table.TableConfig

Fields
------
Customs rendering
^^^^^^^^^^^^^^^^^
Sometimes you may want to render some information of the item in a different
way. This is possible by setting the `renderer` config option and writing a
custom render function.

Example field configuration::

        {"name": "field", "label": "Fieldname", "renderer": "foo.bar.myrenderer"}

The field `field` must exist to prevent warnings while rendering the overview.
However the field does not really matter here as the renderer will get
all informations you may need to to a nice rendering.
The `renderer` refers to a callable which is defined like this::

        from ringo.lib.helpers import literal

        def myrenderer(request, item, column, tableconfig):
            # Do the renderering. In case you return HTML do not forget to
            # escape all values properly and finally return a literal.
            return literal("<strong>Hello world!</strong>")


Sorting
-------
Filters
.......

Overwriting defaults
====================
The behaviour of the application can be modified in different ways. You can
customize the **layout** of forms, overviews and or the whole page layout and
you can customize the **logic** of your application.

There are basically two ways to customize your application:

 1. Overwriting defaults to customize existing behavior.
 2. Extending existing application logic


.. rubric:: Defaults in Ringo

If you have created a new application you may wonder that there are so less
files generated. There are no views generated, no templates and you can not
find any static files.

There reason for that is that ringo is using its defaults for the new
application: 

 1. Views for all modules including the basic CRUD actions has been configured
     on application start. They all use the base default actions defined in
     Ringo.
 2. Templates, form configurations, overview configuration and translations
     are searched in different locations. Actually on each request ringo tries
     to load a more specific version of a template but falls back to the ringo
     default as long as it can not find a

So if you want to customize your application you can overwrite the default.

Overwriting views
-----------------
Application logic is defined in the view function. The view for specific
actions can be overwritten.  In the following example we will overwrite the
default 'index' method of the 'home' view, but this also works for the CRUD
actions of a module. Define your custom method in your view file::

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

.. important::
        Please do not forget to set the permissions checks in the view. If you
        overwrite a view which requires update permissions you **must** set
        this permission again in the view. Otherwise the permission check is
        disabled.
        To add a permission check you can add an `permission` attribute to the
        `view_config` call with the name of the required permisson in lower
        case::

                @view_config(route_name='item-update', renderer='/update.mako', permission="update")
                ...

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

.. rubric:: Using callbacks in the views

Callbacks can be used to implement custom application logic after the logic of
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

The request and the item should give you all the context you should need to to the
desired modifications.

However the preferred way to implement callbacks is wrapping your callable in
a using the callback class with allows you to add more informations to
configure its behavior.::

        from ringo.views.callbacks import Callback
        my_callback = Callback(foo_callback, mode="pre")

This way to define the callback let you set time of execution of the callback
while processing the actual view. See :mod:`ringo.views.callbacks` for more
information.

The callback must be supplied in the call of the main view function like
this::

        @view_config(route_name=Foo.get_action_routename('create'),
                renderer='/default/create.mako',
                permission='create')
        def create(request):
                return create_(Foo, request, callback=foo_callback)

In case you write your custom view and want to handle  the callback you should
use the :func:`ringo.views.request.handle_callback` method.::

        handle_callback(request, callback, item=item, mode="pre")
        # Do the real action
        handle_callback(request, callback, item=item, mode="post")

.. versionadded:: 1.2.2
        The callback can now optionally be a list of callback functions. This
        can be used to stack multiple callbacks.

Overwriting static files 
------------------------
Static files are templates, form and overview configurations.
To overwrite the default simply copy the file from ringo into your application
with the same name at the same location. Now you can do the modifications in
the copied file. 

.. hint::
        In case you want to overwrite the forms checkout formbars inheritance
        and include feature if you only want to do small changes.

After that restart ringo so that ringo knows about new files
it should consider to load. On the next request you application should load
the overwritten version of the file.


Overwriting translations 
------------------------

Add custom logo
---------------

Custom CSS
----------

Custom Javascript
-----------------


.. _add_view:

Adding views
============
There is almost no ringo specific magic on adding new views to the application
to implement new functionality. Adding new views is basically pure Pyramid as
described in the `Pyramid documentation on view configuration
<http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/viewconfig.html#adding-view-configuration-using-the-view-config-decorator>`_. 

So just create a new view callable and configure it with the '@view_config'::

        from pyramid.view import view_config

        @view_config(route_name='fooroute', renderer='/foo.mako')
        def foo(request):
                # Do the work and return values which are available in the
                # template as # dictionary
                return {}

and add the route configuration in the '__init__.py' file of your
application::

        config.add_route('fooroute', 'path/to/foo/view')

Often you want to to do something with items of a modul. When using a simple
view the item is not already part of the request on default. This can be
changed by defining a ressource factory which will load the item. In the following
example a `Foo` item with the given id in the URL will be loaded and is 
available in the item as `request.item`.::

        from ringo.resources import get_resource_factory
        from app.model.foo import Foo

        config.add_route('fooroute', 'path/to/foo/view/{id}',
                         factory=get_resource_factory(Foo))


The `home.py view
<https://github.com/ringo-framework/ringo/blob/master/ringo/views/home.py>`_
is a good starting point to see how a simple view is added to Ringo.

However there are some limitations on views. This is because they are not so deeply
integrated into the ringo framework. They are a quick way to add some
functionality which the following drawbacks:

1. Permissions to call the view can not configured by setting permissions in
   the rolesystem. Permission checks need to be implemented within the view.
   See :ref:`add_view_permission` for more details.

2. The view can not be displayed in the action bundle, or the context menu of
   a single item. You need to make the view available by either adding a
   link in a template (:ref:`add_view_totemplate`) or as button in the form
   (:ref:`add_view_toform`) on your own.

If one or more points are crucial for you then you might want to 
:ref:`add_action`.

.. _add_view_permission:

Setting permissions
--------------------
Permisson related methods are defined in `lib.security`.
Here is an example of how to check if the current user is allowed to read a
certain item::

        import pyramid.httpexceptions as exc
        from ringo.lib.security import has_permission
        from app.model.foo import Foo

        def foo(request):
            item_id = request.params.get("id")
            factory = Foo.get_item_factory()
            item = factory.load(item_id)
            # You can check for one of the known CRUD actions. It will be
            checked against the permissions of the current user in the
            request.
            if not has_permission("read", item, request):
                raise exc.HTTPForbidden()
            # continue...
            return {}

Make sure you do the permission check as the very first thing in the view.

.. _add_view_toform:

Call view from within forms
---------------------------
Calling a view in the form is basically done in the same way as described in
:ref:`add_view_totemplate`. You will utilize the `HtmlRenderer of formbar
<http://formbar.readthedocs.io/en/latest/config.html#html>`_ to render the
link.


.. _add_view_totemplate:

Call view from template
-----------------------
Assuming you have configured a new view with the routename `myroutename` than
the example code to render a link as a button in the following goes like this::

        <a href="${request.route_path('myroutename')}" class="btn btn-primary">Click me</a> 

Custom authorisation
====================
If you need to change the way Ringo builds the ACL on default you can change this behavior by 
overwriting the ``_get_permissions`` class method of the BaseItem in your model::

    from pyramid.security import Allow

    @classmethod
    def _get_permissions(cls, modul, item, request):

        # Default ACL. Direct access
        permissions = BaseItem._get_permissions(modul, item, request)

        # The default permissions are configured using the setting from the
        # roles. We can now modifiy/extend the default permissions. In the
        # following example we allow of users with role "foo" to read the
        # item
        permissions.append((Allow, 'role:foo', 'read'))

        # An alternativ can be to allow a specific user (by its id/uid) to
        # access the item
        if has_role(request.user, 'foo'):
            uid = request.user.id 
            permissions.append((Allow, 'uid:{}'.format(uid), 'read'))

        return permissions

Ownership inheritance
=====================
It is possible inherit the ownership (uid, gid) of a element from a
related element when *saving* the item. Inheritance of ownership means to
set the ownership of the item based on the  ownership of another item
and **not** with the uid, gid of the current user or other permission
settings like default groups.

.. note::
    Setting the inherited uid or gid only happens when saving the item
    explicit using the `save` method of the BaseItem. On default this is
    only the case when creating new items.

A typicall usecase is to grant users access to the item if they are
allowed to access a related (often parent) item by inheriting the uid
and gid.

To inherit the ownership you must set a special attribute in the model::

    class Foo(BaseItem):
        _inherit_gid = "parent"
        _inherit_uid = "parent"

        ...
        parent = sa.orm.relation(Bar)

You need to define the name of the relation to the item where the uid
and gid will be taken from. Please note that you can also set only one
of the attibutes.

Inheritance from other applications
===================================
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

       import bar.model

This will ensure that all the model will be available to alembic. Otherwise
many tables would be scheduled for a drop.

4. Set the configuration variable `app.base` to ''foo''.
See :ref:`config_app_base` for more details.

5. The initialisation of the database is a little bit different as we want to
initialize the database with the migration scripts and fixtures of ''Foo''::

        bar-admin db init --base foo
        bar-admin fixtures load --app foo

While the migration scripts are copied from foo to bar when initialising the
database for the first time, the fixtures are not! The bar application only
includes the fixtures from the base ringo application. If you want to use the
fixtures from foo on default, then you need to copy the files yourself::

        rm </path/to/bar/>/bar/fixtures/*
        cp -r <path/to/foo/>/foo/fixtures/* </path/to/bar/>/bar/fixtures


Voilà! That is it.

Internationalisation I18n
=========================
Ringo uses the `Babel <http://babel.pocoo.org/docs/>`_ package for handling the message catalogs. Translation of Ringo and Ringo based applications can be done with the following steps.
First move into your application root folder and invoke the following command to extract all messages which should be translated::
    
	python setup.py extract_messages
	
This will generate a new pot-File. Now update the catalogs of the different languages. Please note the '-N' flag to tell babel to be not to smart about fuzzy strings in the translation::
	
	python setup.py update_catalog -N
	
It is now time to edit the generated message catalaog and to put in the missing translations. Finally call the following command to actually compile the translations and to make them available in your application::
	
	python setup.py compile_catalog
	
Further information of the process of internationalisation in a Pyramid application can be found on `i18n in Pyramid <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/i18n.html>`_
	
.. Ringo translation is managed using `the Transifex webservice <https://www.transifex.com/projects/p/ringo/>`_

