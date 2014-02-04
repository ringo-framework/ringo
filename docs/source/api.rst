API
***

Model
=====
BaseItem
--------
.. autoclass:: ringo.model.base.BaseList
.. autoclass:: ringo.model.base.BaseFactory
.. autoclass:: ringo.model.base.BaseItem
Modul
-----
.. autoclass:: ringo.model.modul.ModulItem

Usermanagement
--------------
.. autoclass:: ringo.model.user.User
.. autoclass:: ringo.model.user.Usergroup
.. autoclass:: ringo.model.user.Role
.. autoclass:: ringo.model.user.Profile

News
----
.. autoclass:: ringo.model.news.News

Appointment
-----------
.. autoclass:: ringo.model.appointment.Appointment
.. autoclass:: ringo.model.appointment.Reminders

File
----
.. autoclass:: ringo.model.file.File

Log
---
.. autoclass:: ringo.model.log.Log

Tag
---
.. autoclass:: ringo.model.tag.Tag

Todo
----
.. autoclass:: ringo.model.todo.Todo

Comment
-------
.. autoclass:: ringo.model.comment.Comment

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
