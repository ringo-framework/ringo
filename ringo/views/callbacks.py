#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Implements Callbacks to be used in views to inject custom
functionality into the workflow of the existing (often default CRUD
actions) views.

Depending on the view where the callback is injected the callback is
called before or after the actual action is executed.

The most simple callback possible is defined as::

    def simple_callback(request, item):
        # Do something with the item and finally return the item.
        return item

Beside of this be simple callback you can implement a callback by
inheriting from one of the classes within this modul to implement more
complex application logic.

Please note, that the view must support handling calling callback
instances and make use of the extra values which can be set within the
callback.
"""


class Callback(object):

    """Callback class to implement more complex execution workflows.
    Every callback has a `mode` that defines the time when the callback is
    called during the view execution. This can either be before the
    actual action (pre) or after it (post). By setting this mode you can
    define when to call the callback. On default the execution time is
    defined in the view."""

    def __init__(self, callback, mode=None):
        """Init the callback and configure its behaviour.

        :callback: Callable which is used as callback
        :mode: 'pre' or 'post' or None
        """

        self.callback = callback
        if mode not in ["pre", "post", None]:
            raise ValueError("Mode can either be None, `pre` or `post`")
        self.mode = mode

    def __call__(self, request, item):
        return self.callback(request, item)
