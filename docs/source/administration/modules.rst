.. _modul_configuration:

*******************
Modul Configuration
*******************

The modul modul is used to administrate the moduls within Ringo. It is only
available for user with the role "admin".

.. image:: ../screenshots/modul.png
   :width: 800
   :alt: Edit dialog of a modul.

The screenshot shows the Edit-Dialog for a role.

 * Name: This is the internal name of the modul. It is a required field and must be unique in the system.
 * Label singular: This is the label used for single items of the modul.
 * Label plural: This is the label used for multiple items of the modul (Overviews).
 * Description: A textual description of the modul.
 * String representation: The string representation defines how items of the modul are displayed as a single string like in selection lists.
 * Actions: A list of actions which are available for the Modul. This way you can disable an action complete. Not enabled action will not be listed anywhere.

.. _modul_configuration_display:
Display of the module
=====================
You can choose there to disply the modul in your UI. You can display the modul
in one of the following places:

 * :ref:`ui_mainmenu`
 * :ref:`ui_usermenu`
 * :ref:`ui_adminmenu`

Select hide to hide the modul completely
