******************
Elements of the UI
******************
This chapter will give an overview of user elements in the basic ringo user
interface (UI) and how to use them.

.. warning::
        The screenshots are outdated!

Below you can see an example of a view in the Ringo application.


.. image:: ../screenshots/home.png
   :width: 800
   :alt: Ringo after login 

The Ringo UI is divided into three areas. In the top there is a header. At the
bottom the footer and in the middle there is the content.

Main Menu
=========
The Main Menu will list the link to the :ref:`ui-home` page of your
application and a entry for all available and enabled non administrational
:ref:`modules`. The links will usually link the :ref:`ui-overview` page of the
selected modul.

.. image:: ../screenshots/ui/mainmenu.png

The currently active modul is highlighted.

.. _ui-user-menu:

User Menu
=========

The User Menu is only visible for logged in users. The Menu will give access
to user specific functions.

.. image:: ../screenshots/ui/usermenu.png

The label of the menu shows the login name of the currently logged in user.
These are:

 * Profil: Will open the Profil of the user.
 * Change Password: Will open a dialog to change the users password.
 * Logout: Will logout the user

Context Menu
============
The context menu will provide available actions for the currently selected
item, or more generally speaking for the currently displayed page.

The available actions can be configured in the :ref:`modul-modul` administration.

.. image:: ../screenshots/ui/contextmenu.png

The following actions are currently availabe in Ringo. Listed from left to right:

 1. Overview: Go back to the overview of the modul.
 2. Add new item: Will open the page to create a new item of the modul.
 3. Read item: Will open the currently selected item in read only mode.
 4. Edit item: Will open the currently selected item in edit mode.
 5. Delete item: Will delete the currently selected item.

Administraion Menu
==================

.. image:: ../screenshots/ui/administrationmenu.png

The Administraion Menu is only visible for users with the "admin" role after
login. It gives access to the administration of the modules.

.. _ui-footermenu:

Footer Menu
===========

.. image:: ../screenshots/ui/footermenu.png

The Footer menu gives general information on your application like how to
contact you or version information.
