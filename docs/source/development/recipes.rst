***********************
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

Overwriting static files
========================
Simply place the modified file with the same name in the application.

Configuring forms
=================
Simply overwrite the form configuration in your application

Configuring overviews
=====================
Simply overwrite the table configuration in your application


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
