*******************
User Administration
*******************


User
====
The user modul is used to administrate the users within Ringo. It is only
available for user with the role "admin".

.. image:: ../screenshots/user.png
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

.. image:: ../screenshots/profile.png
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

.. image:: ../screenshots/usergroup.png
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

.. image:: ../screenshots/role.png
   :width: 800
   :alt: Edit dialog of a role.

The screenshot shows the Edit-Dialog for a role.

 * Name: This is the name for the role. It is a required field and must be unique in the system.
 * Permissions: Each role can be assigned the permissions to different actions of the moduls in the system. You can select one or more actions from a listing of available and configured actions from the :ref:`modul-modul`. Users with this role will be allowed to call the action.
 * Administrational role: This flag indicates that this role is an administrational role which means that the user will have permission to call the configured actions without checking the ownership of the item.
