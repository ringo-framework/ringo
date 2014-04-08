"""
Ringo offers the option to equip items of the modules with a
one or more state machines to model statefull workflows.

An classical example for a statefull workflow is a process where an item
can be in an `draft`, `review` and `published` state.

The statemachine offers features like

 * Restrictions on access
 * Conditional transitions
 * Handlers.

Depending on the state the state machine can be configured to restrict
access to the item for certain users. Further you can define conditions
which must be true before the state can switch into another. Finally you
can write certain handlers which are called right after the state has
changed.

A state machine can be attached to the items using a :ref:`mixin_state`
which organises the state machines an provides a unique interface.
"""

def walk(state, found=None):
    """Helper function to collect all available states in the states
    graph beginning from the given start state

    :state: Start state
    :returns: List of all states

    """
    if not found:
        found = []
    if state not in found:
        found.append(state)
        for transition in state.get_transitions():
            if transition._end_state in found:
                continue
            else:
                walk(transition._end_state, found)
    return found


def null_handler(item, transition):
    """Null handler"""
    return item


def null_condition(item, transition):
    """Null condition"""
    return True

class TransitionHandler(object):

    """Handler callable which will be called if the transition between
    to :class:`State` objects has been finished."""

    def __call__(self, item, transition):
        """Implement me!

        :item: :class:`BaseItem` instance
        :returns: :class:`BaseItem` instance

        """
        return null_handler(item, transition)

class TransitionCondition(object):

    """Condition callable which must be true to make the :class:`Transition`
    between two :class:`State` objects applicable."""

    def __call__(self, item):
        """Implement me!

        :item: :class:`BaseItem` instance
        :returns: True or False

        """
        return null_condition(item, transition)

class Statemachine(object):
    """A state machine, is a mathematical model of computation used to
    design sequential logic circuits for items of a module. It is
    conceived as an abstract machine that can be in one of a finite
    number of states.  The machine is in only one state at a time; the
    state it is in at any given time is called the current state. It can
    change from one state to another when initiated by a triggering
    event or condition; this is called a transition."""

    def __init__(self, item, item_state_attr, init_state=None, request=None):
        """Initialise the statemachine for the given item.

        :item: Attach the state machine to this :class:`BaseItem`
        :item_state_attr: name of the attribute which store the value of
        the current state of the statemachine in the given item.
        :init_state: Initialize the statemachine with an alternative
        state. (Not the value coming from item_state_attr)
        :request: Current request.

        """
        self._item = item
        self._item_state_attr = item_state_attr
        self._root = self.setup()
        self._current = self._root
        self._request = request

        # Try to set the current state of the statemaching by getting
        # the current state from the item.
        current_id = getattr(self._item, self._item_state_attr)
        if init_state:
            current_id = init_state
        for st in self.get_states():
            if st._id == current_id:
                self._current = st
                break

    def setup(self):
        """Need to be implemented in the inherited class.

        Example::

            s1 = State(self, 1, "On")
            s2 = State(self, 2, "Off")

            s1.add_transition(s2, "Turn on", handler, condition)
            s2.add_transition(s1, "Turn off", handler, condition)
            return s1
        """
        return None

    def get_states(self):
        """Returns a list of all states in the statemachine

        :returns: List of :class:`State` objects.

        """
        return walk(self._root)

    def set_state(self, state):
        """Will set the current state of the state machine

        :state: Id of the :class:`State` or the :class:`State` object to
        be set as current state
        :returns: None

        """
        for transition in self._current.get_transitions():
            if (transition._end_state._id == state or
               transition._end_state == state):
                self._item = transition._handler(self._item, transition)
                self._current = transition._end_state
                setattr(self._item, self._item_state_attr, self._current._id)
                return self._current
        raise Exception('No fitting transition to transition found')

    def get_state(self):
        """Returns the current state of the Statemachine

        :returns: Current :class:`State`

        """
        return self._current


class Transition(object):
    """A transitions is used to switch from one state into another. The
    two states are called start state and end state where the end state
    is the state of the state machine after the transtions has been
    done.

    Every transtion can have a handler and a condition. The handler can
    be used to add some logic which should be trigger after the
    transition has been finished. The handler is a simple callable which
    is called with the item of the state machine.

    The condition is also a callable and can be used to restrict the
    availability to whatever want. The function is called with the item
    of the state machine and returns true or false. If the condition
    returns true then a transition is available."""

    def __init__(self, start_state, end_state,
                 label=None, handler=None, condition=None):
        """Creates a transition between to states.

        :start_state: Start :class:`State` of the transition
        :end_state: End of the transition
        :handler: :class:`TransitionHandler` which will be called if the state has
                  been changed
        :condition: :class:`TransitionCondition` which must be true to make the
                    transition available

        """
        self._label = label
        self._start_state = start_state
        self._end_state = end_state
        self._handler = handler
        self._condition = condition

    def get_start(self):
        """Returns the start state of the transition

        :returns: Start :class:`State`

        """
        return self._start_state

    def get_end(self):
        """Returns the end state of the transition

        :returns: End :class:`State`

        """
        return self._end_state

    def get_label(self):
        """Returns the label of the transtion. If no label was set
        return the two lables of the start and end state separated with
        a "->".

        :returns: Label of the :class:`State`

        """
        if self._label:
            return self._label
        else:
            return "%s -> %s" % (self._start_state._label,
                                 self._end_state._label)

    def exchange(self):
        """Do the transition! Exchanges the start state to the end state.

        :returns: End :class:`State` of the transtion.

        """
        if self.is_available():
            state = self.get_end()
            return state
        else:
            raise Exception("Change of state failed")

    def is_available(self):
        """Check is the transition is available for the item in the
        statemachine. The function will call the condition function with
        the item of the statemachine. It returns true if the state is
        available (check succeeds) and returns False if the conditions
        for a state change are not met."""
        if self._condition:
            return self._condition(self.get_start()._statemachine._item, self)
        else:
            return True


class State(object):
    """A single state in a statemachine."""

    def __str__(self):
        return self._label

    def __init__(self, statemachine, id, label,
                 description=None, disabled_actions={}):
        """Initialise the State

        :statemachine: Statemachine
        :id: Id of the state
        :label: Label of the Statemachine (short description)
        :description: Long description of the state.
        :disabled_actions: Dictionary with a list of actions which are
        disabled for a role. {'rolename': ['read', 'update']}

        """
        self._statemachine = statemachine
        self._id = id
        self._label = label
        self._description = description
        self._disabled_actions= disabled_actions
        self._transitions = []

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self._label

    def add_transition(self, to_state, label=None,
                      handler=None, condition=None):
        """Will add a transtion to the given state

        :to_state: End state of the transition
        :label: Label of the transition. Is usually a verb.
        :handler: :class:`TransitionHandler` which will be called if the state has
                  been changed
        :condition: :class:`TransitionCondition` which must be true to make the
                    transition available
        :returns: None

        """
        trans = Transition(self, to_state, label, handler, condition)
        self._transitions.append(trans)

    def get_disabled_actions(self, role):
        """Returns a list of disabled actions of the state for the given
        role

        :returns: List of disabled actions

        """
        return self._disabled_actions.get(role, [])

    def get_transitions(self):
        """Returns the available transitions to other states.

        :returns:  List of :class:`Transition` objects.

        """
        transitions = []
        for trans in self._transitions:
            if trans.is_available():
                transitions.append(trans)
        return transitions
