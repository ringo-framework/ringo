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
    pass


class Statemachine(object):
    """Statemachine class"""

    def __init__(self, item, start, current=None):
        """Initialise the statemachine for the given item and provide
        the start state of the machine and optionally the current state.
        If the current state is not set then the start state is set as
        current state."""
        self._item = item
        self._start = start
        self._current = current
        if not current:
            self._current = start

    def get_states(self):
        """Returns a list of all states in the statemachine
        :returns: List of states.

        """
        return walk(self._start)

    def set_state(self, state):
        """Will set the current state of the state machine

        :state: State to be set as current state
        :returns: None

        """
        for transition in self._current.get_transitions():
            if transition._end_state == state:
                transition._handler(self._item)
                self._current = state
                return self._current
        raise Exception('No fitting transition to transition found')

    def get_state(self):
        """Returns the current state of the Statemachine
        :returns: State

        """
        return self._current


class Transition(object):
    """A class for transitions between to states"""

    def __init__(self, start_state, end_state, label=None, handler=None):
        """Creates a transition between to states.

        :start_state: @todo
        :end_state: @todo
        :handler: @todo

        """
        self._label = label
        self._start_state = start_state
        self._end_state = end_state
        self._handler = handler

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
        return self.get_end()


class State(object):
    """Docstring for State """

    def __init__(self, id, label):
        """@todo: to be defined

        :id: @todo
        :label: @todo

        """
        self._id = id
        self._label = label
        self._transitions = []

    def add_transition(self, to_state, label=None, handler=None):
        trans = Transition(self, to_state, label, handler)
        self._transitions.append(trans)

    def get_transitions(self):
        """Returns the available transitions to other states.
        :returns:  List of Transitions.

        """
        return self._transitions
