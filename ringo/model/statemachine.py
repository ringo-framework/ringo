"""A state machine, is a mathematical model of computation used to
design sequential logic circuits for items of a module. It is conceived
as an abstract machine that can be in one of a finite number of states.
The machine is in only one state at a time; the state it is in at any
given time is called the current state. It can change from one state to
another when initiated by a triggering event or condition; this is
called a transition.
"""

def walk(state, found=[]):
    """Helper function to collect all available states in the states
    graph beginning from the given start state

    :state: Start state
    :returns: List of all states

    """
    if state not in found:
        found.append(state)
    for transition in state.get_transitions():
        if transition._end_state in found:
            continue
        else:
            found.append(transition._end_state)
            found = walk(transition._end_state, found)
    return found


def null_handler(item):
    return item


def null_condition(item):
    return True


class Statemachine(object):
    """The class for the statemachine"""

    def __init__(self, item, key_state_id):
        """Initialise the statemachine for the given item."""
        self._item = item
        self._key_state_id = key_state_id
        self._root = self.setup()
        self._current = self._root

        # Try to set the current state of the statemaching by getting
        # the current state from the item.
        for st in self.get_states():
            if st._id == getattr(self._item, self._key_state_id):
                self._current = st
                break

    def setup(self):
        """Need to be implemented in the inherited class. Example::

            s1 = State(self, 1, "On")
            s2 = State(self, 2, "Off")

            s1.add_transition(s2, "Turn on", handler, condition)
            s2.add_transition(s1, "Turn off", handler, condition)
            return s1
        """
        return None

    def get_states(self):
        """Returns a list of all states in the statemachine
        :returns: List of states.

        """
        return walk(self._root)

    def set_state(self, state):
        """Will set the current state of the state machine

        :state: State id of the state or state item to be set as current
        state
        :returns: None

        """
        for transition in self._current.get_transitions():
            if (transition._end_state._id == state or
               transition._end_state == state):
                self._item = transition._handler(self._item)
                self._current = transition._end_state
                setattr(self._item, self._key_state_id, self._current._id)
                return self._current
        raise Exception('No fitting transition to transition found')

    def get_state(self):
        """Returns the current state of the Statemachine
        :returns: State

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

        :start_state: @todo
        :end_state: @todo
        :handler: @todo
        :condition: @todo

        """
        self._label = label
        self._start_state = start_state
        self._end_state = end_state
        self._handler = handler
        self._condition = condition

    def get_start(self):
        """Returns the start state of the transition
        :returns: State
        """
        return self._start_state

    def get_end(self):
        """Returns the end state of the transition
        :returns: State
        """
        return self._end_state

    def get_label(self):
        """Returns the label of the transtion. If no label was set
        return the two lables of the start and end state separated with
        a "->".
        :returns: String of the label
        """
        if self._label:
            return self._label
        else:
            return "%s -> %s" % (self._start_state._label,
                                 self._end_state._label)

    def exchange(self):
        """Exchanges the start state to the end state.
        :returns: End state of the transtion.
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
            return self._condition(self.get_start()._statemachine._item)
        else:
            return True


class State(object):
    """A single state in a statemachine."""

    def __init__(self, statemachine, id, label,
                 description=None, disabled_actions={}):
        """@todo: to be defined

        :statemachine: @todo
        :id: @todo
        :label: @todo
        :description: @todo
        :disabled_actions: @todo

        """
        self._statemachine = statemachine
        self._id = id
        self._label = label
        self._description = description
        self._disabled_actions= disabled_actions
        self._transitions = []

    def add_transition(self, to_state, label=None,
                       handler=None, condition=None):
        trans = Transition(self, to_state, label, handler, condition)
        self._transitions.append(trans)

    def get_disabled_actions(self, role):
        """Returns a list of disabled actions of the state for the given
        role"""
        return self._disabled_actions.get(role, [])

    def get_transitions(self):
        """Returns the available transitions to other states.
        :returns:  List of Transitions.

        """
        # Check if the
        transitions = []
        for trans in self._transitions:
            if trans.is_available():
                transitions.append(trans)
        return transitions