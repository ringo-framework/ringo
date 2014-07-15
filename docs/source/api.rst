API
***

Model
=====

BaseList
--------
.. autoclass:: ringo.model.base.BaseList
   :members:

BaseFactory
-----------
.. autoclass:: ringo.model.base.BaseFactory
   :members:

BaseItem
--------
.. autoclass:: ringo.model.base.BaseItem
   :members:

Modul
-----
.. autoclass:: ringo.model.modul.ModulItem
   :members:
.. autoclass:: ringo.model.modul.ActionItem
   :members:

.. _api-usermanagement:

Usermanagement
--------------
.. autoclass:: ringo.model.user.User
   :members:
.. autoclass:: ringo.model.user.Usergroup
   :members:
.. autoclass:: ringo.model.user.Role
   :members:
.. autoclass:: ringo.model.user.Profile
   :members:

News
----
.. autoclass:: ringo.model.news.News
   :members:

Appointment
-----------
.. autoclass:: ringo.model.appointment.Appointment
   :members:
.. autoclass:: ringo.model.appointment.Reminders
   :members:

File
----
.. autoclass:: ringo.model.file.File
   :members:

Log
---
.. autoclass:: ringo.model.log.Log
   :members:

Tag
---
.. autoclass:: ringo.model.tag.Tag
   :members:

Todo
----
.. autoclass:: ringo.model.todo.Todo
   :members:

Comment
-------
.. autoclass:: ringo.model.comment.Comment
   :members:

.. _api-statemachine:

Statemachine
------------
.. autoclass:: ringo.model.statemachine.Statemachine
   :members:
.. autoclass:: ringo.model.statemachine.State
   :members:

.. autoclass:: ringo.model.statemachine.Transition
   :members:
.. autoclass:: ringo.model.statemachine.TransitionHandler
.. autoclass:: ringo.model.statemachine.TransitionCondition

Lib
===

.. _api-security:

Security
--------
.. autofunction:: ringo.lib.security.has_permission
.. autofunction:: ringo.lib.security.get_permissions
.. autofunction:: ringo.lib.security.get_principals
.. autofunction:: ringo.lib.security.has_role
.. autofunction:: ringo.lib.security.get_roles
.. autofunction:: ringo.lib.security.has_group
