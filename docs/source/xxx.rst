Ringo
#####
This is the documentation of the Ringo application framework. After a short overview we
will explain the user interface and some basic concepts in Ringo.

Overview
********
Get an overview of Ringo. Know what it is, which features can be expected,
licensing and finally how to install it.

What is Ringo?
==============
Ringo is a small Python based high level web application framework build with
Pyramid . It provides basic functionality which is often used in modern web
applications. See the list of :ref:`features` for more details.

Ringo comes with an application scaffold which can be used as a boilerplate for
your application development. See the :ref:`development` part for more details on how
to build a Ringo based application.

In Ringo based applications Ringo plays the role of a base library which
provides basic functionality. In most cases this basic functionality should
fit the needs in easy usecases. If it fits not, then it can be extended and
configured to your need in an easy way.

Ringo is also a standalone application which is under steady development. This
is a benefit if you use Ringo as base for your application. Your application
will get bug fixes, new features or improved functionality in most cases by simply
updating Ringo to a new version.

License
=======
Ringo is Free Software. It is licensed under the GPL license in version 2 or
later. See `<http://www.gnu.org/licenses/gpl-2.0>`_ for more details on the license.

.. _features:

Features
========
Ringo provides some basic features which are useful if you build your
web application based on Ringo:

 * Authentication with email registration and password reminders
 * Authorisation with a role based permission System
 * Basic CRUD actions
 * Layout and validation of forms using the `Formbar <https://pypi.python.org/pypi/formbar>`_ library
 * Support for caching expensive SQL queries
 * Regular expression based searching (storeable)
 * Sorting
 * User Profiles
 * Extendible, Configurable

.. _installation_production:

Installation
============
Ringo is available in its latest stable version on `PyPi <https://pypi.org/toirl/ringo>`_::

        pip install Ringo

The source code is also available on `Bitbucket <https://bitbucket.org/ti/ringo>`_ if you want to keep track of
the latest development version::

        hg clone https://bitbucket.org/ti/ringo
        cd ringo
        python setup.py install

You probably want to continue to read the :ref:`development` section to learn
how to setup Ringo based application.

Requirements
------------
Ringo was developed within a Python 2.7.3 environment. Older versions will not
work as Ringo uses some XML features only available in Python >= 2.7.3. Newer
versions might work, but it is not tested.

Contact
=======
You can contact the author by his email address "torsten at irlaender dot de".
In case of bugs and feature requests please open a ticket on Bitbucket.

UI
**
This section will explain the User Interface of Ringo. This will introduce
some Ringo specific terminology which is used later in the documentation.


Below you can see an example of a view in the Ringo application.


.. image:: screenshots/home.png
   :width: 800
   :alt: Ringo after login 

The Ringo UI is divided into three areas. In the top there is a header. At the
bottom the footer and in the middle there is the content.

Header
======
The header is at the top of the page an includes name of the application, the :ref:`ui-main-menu` and the
:ref:`ui-user-menu`.

.. _ui-main-menu:

Main Menu
---------
The Main Menu will list the link to the :ref:`ui-home` page of your
application and a entry for all available and enabled non administrational
:ref:`modules`. The links will usually link the :ref:`ui-overview` page of the
selected modul.

.. image:: screenshots/ui/mainmenu.png

The currently active modul is highlighted.

.. _ui-user-menu:

User Menu
---------

The User Menu is only visible for logged in users. The Menu will give access
to user specific functions.

.. image:: screenshots/ui/usermenu.png

The label of the menu shows the login name of the currently logged in user.
These are:

 * Profil: Will open the Profil of the user.
 * Logout: Will logout the user

Main
====
The section is used to display the main content in your application. Each page
which is displayed here will usually have a header which gives information on
what you are currently viewing. In the header there is also a context menu on
the right side.

Context Menu
------------
The context menu will provide available actions for the currently selected
item, or more generally speaking for the currently displayed page.

The available actions can be configured in the :ref:`modul-modul` administration.

.. image:: screenshots/ui/contextmenu.png

The following actions are currently availabe in Ringo. Listed from left to right:

 1. Overview: Go back to the overview of the modul.
 2. Add new item: Will open the page to create a new item of the modul.
 3. Read item: Will open the currently selected item in read only mode.
 4. Edit item: Will open the currently selected item in edit mode.
 5. Delete item: Will delete the currently selected item.

.. _ui-home:

Home
----
The home page is the entry page of your application and will give you an
overview of the most important news in your application like appointments, new
entries, or some statistics. However in Ringo this page is empty and it is up
to you to fill it with content.

.. _ui-overview:

Overview
--------
Each modul has an overview page which lists all items of the modul. Each
overview provides the following functionality:

 1. Sorting
 2. Searching
 3. more will to be implemented...

.. image:: screenshots/ui/search.png

To open one of the shown items in the overview you can click simple somewhere
in the row. The item will be opened in read mode. Note that you need to click
on the row and not on the value as this triggers a search. See more details below.

Sorting
```````
The header of the overview table is clickable to sort the listing on the
selected header. Clicking on the header toggles between ascending and
descending sorting. A small icon shown on which column the sorting was done.

Searching
`````````
The search is based on the visible values in the overview. That means you can
search for anything which is displayed in one of the columns. If the search
string matches at least one value in the column the item will be found and
displayed in the overview.

The search can be a regular expression. Optionally you can select a specific
column to restrict the search an this column. On default the search is done
over all visible columns.

.. hint::
   You can also a search by clicking on the literal value in a column. This
   will trigger a new search for the clicked value in the corresponding
   column.

The search is stackable. This way you can narrow down your search by refining
your search by doing another search on the last search result. You can see how
many filters are currently applied next to the options drop-down.
To pop the last filter from the search stack simply enter a empty search.
To reset the whole search stack at once select the "Reset current search
filter" option from the options drop-down.

You can save your current search under a user defined query name and make it
available for later use. This becomes very handy if you are in the need of
some often used predefined searches.

.. note::
   You can only save a search which actually has at least one found item in
   the search result. Further the name for your query must be unique. It is
   not possible to edit a saved search. You need to save it under a new name.

To save the current search stack, select the "Search current search stack"
option from the options drop-down. You can enter your desired name for the
query and then save it in your user settings.
The saved searches are then listed in the options dropdown. You can delete a
saved search by clicking on the cross symbol next to each filter.



Footer
======
At the bottom of the screen is the footer which provides access to the
:ref:`ui-administrationmenu` and :ref:`ui-footermenu`.

.. _ui-administrationmenu:

Administraion Menu
------------------

.. image:: screenshots/ui/administrationmenu.png

The Administraion Menu is only visible for users with the "admin" role after
login. It gives access to the administration of the modules.

.. _ui-footermenu:

Footer Menu
-----------

.. image:: screenshots/ui/footermenu.png

The Footer menu gives general information on your application like how to
contact you or version information.

.. _modules:

Modules
*******
Ringo uses the term "Modul" to describe different data (data types) in your
application.  Ringo comes with some predefined modules for users, usergroups,
roles and the modules itself.  Each of those moduls provide an interface with
basic CRUD functionality of work witch items of a modul.

Moduls also define some meta data on the data like which actions (Create,
Read, Update, Delete...) are available, labels, visibility etc.  Further the
authorisation is bound to the moduls too and defines and which users are
allowed to use the configured actions.

If there is any data in the application which needs to be created by the user
and stored permanently in the database it is very likely done within a modul.

Example:: Think of an application to organise your orders in a shopping
application e.g. So you will have to store customers, articles, orders, prices,
addresses etc. Each of those will be its own modul.

See :ref:`commands` for more information on how to add new moduls to your
application.

.. _modul-users:

User
====
The user modul is used to administrate the users within Ringo. It is only
available for user with the role "admin".

.. image:: screenshots/user.png
   :width: 800
   :alt: Edit dialog of a user.

The screenshot shows the Edit-Dialog for a user.

 * Login: This is the login name for the user. It is a required field and must be unique in the system.
 * Roles: Each user can have different roles assigned. You can select one or more roles for a listing of available items of the :ref:`modul-roles`.
 * Groups: Each user can be member of different groups. The user will inherit all roles assigned to the group. You can select one or more groups for a listing of available items of the :ref:`modul-groups`.
 * Activated: The user can be activated and deactivated which means that the the user can login to the application.
 * Activation Token: In case the the user is deactived you can define an activation token (usually a UUID) which can be used to activate the user.  This field is used while registering a new user. The user needs to confirm the registration by calling an URL with the defined activation token.

.. _modul-profile:

Profile
=======
The profile modul is used to administrate the users profiles in Ringo. It is only
available for user with the role "admin" and the owner of the profile (user
with belongs to the profile).

The profile is used to attach some additional common informations to the users in the system.

Profiles can not be deleted or created. The creation and deletion is done
automatically when creating and deleting the user.

.. image:: screenshots/profile.png
   :width: 800
   :alt: Edit dialog of a profile

The screenshot shows the Edit-Dialog for a profile.

 * Firstname: The first name of the user
 * Lastname: The last name of the user.
 * Birthday: The birthday of the user.
 * Address: A free text field to give the address of the user.
 * Phone: The telephone number.
 * Email: The users email. Is used to send notification mails in the system.
 * Web: A URL to the users web presence.

.. _modul-groups:

Usergroup
=========
The usergroups modul is used to administrate the usergroups within Ringo. It is only
available for user with the role "admin".

Groups can be used to assign a defined set of roles to multiple users. Further
the membership of groups can be a criteria on the permission checks.

.. image:: screenshots/usergroup.png
   :width: 800
   :alt: Edit dialog of a usergroup.

The screenshot shows the Edit-Dialog for a usergroup.

 * Name: This is the name for the usergroups. It is a required field and must be unique in the system.
 * Roles: Each usergroup can have different roles assigned. You can select one or more groups from a listing of available items of the :ref:`modul-roles`. A user will have all the roles of the groups he is member of.
 * Members: Define the members of the usergroup. You can select one or more groups from a listing of available items of the :ref:`modul-users`

.. _modul-roles:

Role
====
The roles modul is used to administrate the usergroups within Ringo. It is only
available for user with the role "admin".

Roles are generally used to bind certain permissions in the application to
different users. Users who have a certain role will gain the defined permissions.
For more information on the authorisation please consult the
:ref:`authorisation` section.

.. image:: screenshots/role.png
   :width: 800
   :alt: Edit dialog of a role.

The screenshot shows the Edit-Dialog for a role.

 * Name: This is the name for the role. It is a required field and must be unique in the system.
 * Permissions: Each role can be assigned the permissions to different actions of the moduls in the system. You can select one or more actions from a listing of available and configured actions from the :ref:`modul-modul`. Users with this role will be allowed to call the action.
 * Administrational role: This flag indicates that this role is an administrational role which means that the user will have permission to call the configured actions without checking the ownership of the item.

.. _modul-modul:

Modul
=====
The modul modul is used to administrate the moduls within Ringo. It is only
available for user with the role "admin".

.. image:: screenshots/modul.png
   :width: 800
   :alt: Edit dialog of a modul.

The screenshot shows the Edit-Dialog for a role.

 * Name: This is the internal name of the modul. It is a required field and must be unique in the system.
 * Label singular: This is the label used for single items of the modul.
 * Label plural: This is the label used for multiple items of the modul (Overviews).
 * Description: A textual description of the modul.
 * String representation: The string representation defines how items of the modul are displayed as a single string like in selection lists.
 * Actions: A list of actions which are available for the Modul. This way you can disable an action complete. Not enabled action will not be listed anywhere.
 * Display: Select the menu where the modul will be listed. Select hide to hide the modul completely

Permission System
*****************

.. _authendtification:

Authentification
================

.. _authorisation:

Authorisation
=============

.. _commands:

Commands
********
Ringo implements some additional commands which can be used on the shell.

add_modul
=========
The "add_modul" command is used to add :ref:`modules` to your application. The
command will do needed database modifications and create some skeleton files
within your projects as boilerplate for further development.

Usage::

        add_ringo_modul --config /path/to/your/application-config.ini NameOfModul

The actual name of the command may vary if you want to add a modul your a
Ringo based application. Please call the command with "--help" option to get a
full list of available options.

.. _development:

Development
###########

How to...
*********
... do XYZ? To help you to get the feet on the ground in Ringo development this section will try to give answers on some of basic questions you might have in the beginning.

.. _installation_development:

Setup a Ringo developmet environment
====================================
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
================
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
===========================================
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

Change various aspects in my Ringo based application
====================================================
Change the name of the application
----------------------------------

API
***
lib
===
.. automodule:: ringo.lib.renderer
   :members:
   :inherited-members:


Tests
*****
Scaffolds
*********

.. _scaffold_basic:

Basic Scaffold
==============
