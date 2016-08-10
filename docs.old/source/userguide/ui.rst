******************
Elements of the UI
******************
This chapter will give an overview of user elements in the basic ringo user
interface (UI).

Below you can see an example of a view in the Ringo application.


.. image:: ../screenshots/ui/ui.png
   :width: 800
   :alt: Default UI of Ringo

1. :ref:`ui_mainmenu`
2. :ref:`ui_usermenu`
3. :ref:`ui_contextmenu`
4. :ref:`ui_adminmenu`
5. :ref:`ui_footer`

.. _ui_mainmenu:

Main Menu
=========
The Main Menu lists the primary modules of the application. Usally clicking on
on the the module entries will take you the the :ref:`userguide_overviews` of
the module.

.. image:: ../screenshots/ui/mainmenu.png

.. _ui_usermenu:

User Menu
=========

The User Menu is only visible for logged in users. The Menu will give access
to user specific functions.

.. image:: ../screenshots/ui/usermenu.png

The label of the menu shows the login name of the currently logged in user.
These are:

 * Profil: Will open the :ref:`usage_profile` of the user.
 * Change Password: Will open a dialog to :ref:`usage_changepassword` of the
   user.
 * Logout: Will logout the user

.. _ui_contextmenu:

Context Menu
============

.. image:: ../screenshots/ui/contextmenu.png

The context menu is devided into two parts. The left part list the primary
CRUD actions of a module. The right part (*Advanced*) is a dropdown menu which gives access
to secondary actions like Import and Export. Depending on your permissions and
the modul configuration there might be other actions available.

.. _ui_adminmenu:

Administration Menu
===================

.. image:: ../screenshots/ui/administrationmenu.png

The Administraion Menu is only visible for users with the "admin" role after
login. It gives access to the administration of the modules.

.. _ui_footer:

Footer Menu
===========

.. image:: ../screenshots/ui/footermenu.png

The Footer menu gives general information on your application like how to
contact you or version information.
