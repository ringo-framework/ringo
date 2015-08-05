#!/usr/bin/python
# -*- coding: utf8 -*-

import unittest
from ringo.model.statemachine import Statemachine, State, \
    null_handler as handler, null_condition as condition


def _testhandler(item, transition):
    item.testdata = "bar"
    return item

def _testcondition(item, transition):
    return False

class DummyItem(object):
    def __init__(self, state=1):
        self.state = state
        self.testdata = "foo"


class DummyStatemachine(Statemachine):

    def setup(self):
        s1 = State(self, 1, "Unconfirmed")
        s2 = State(self, 2, "New")
        s3 = State(self, 3, "Reopend")
        s4 = State(self, 4, "Assigned")
        s5 = State(self, 5, "Resolved")
        s6 = State(self, 6, "Verfified")
        s7 = State(self, 7, "Closed")

        s1.add_transition(s5, "Decline", handler, condition)
        s1.add_transition(s2, "Accept", handler, condition)

        s2.add_transition(s4, "Assign", handler, condition)
        s3.add_transition(s4, "Reassign", handler, condition)

        s4.add_transition(s5, "Resolve", handler, condition)

        s5.add_transition(s4, "Revise", handler, condition)
        s5.add_transition(s6, "Verify", handler, condition)

        s6.add_transition(s7, "Close", _testhandler, condition)
        s6.add_transition(s5, "Reopen", handler, _testcondition)

        s7.add_transition(s3, "Reopen", handler, condition)
        return s1


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.sm = DummyStatemachine(DummyItem(), 'state')

    def test_num_states(self):
        self.assertTrue(len(self.sm.get_states()) == 7)

    def test_s12s2(self):
        state = self.sm.set_state(2)
        self.assertEqual(state._id, 2)

    def test_s1s3(self):
        with self.assertRaises(Exception):
            self.sm.set_state(3)

    def test_s6s7(self):
        self.sm = DummyStatemachine(DummyItem(6), 'state')
        state = self.sm._current
        self.assertEqual(state._id, 6)
        transitions = state.get_transitions()
        state = self.sm.set_state(transitions[0].exchange())
        self.assertEqual(state._id, 7)
        self.assertEqual(self.sm._item.testdata, 'bar')

    def test_s6s8(self):
        self.sm = DummyStatemachine(DummyItem(6), 'state')
        state = self.sm._current
        self.assertEqual(state._id, 6)
        transitions = state.get_transitions()
        self.assertTrue(len(transitions) == 1)

    def test_start_state(self):
        self.sm = DummyStatemachine(DummyItem(2), 'state')
        state = self.sm.get_state()
        self.assertEqual("New", state._label)

    def test_s1_available_transitions(self):
        state = self.sm.get_state()
        transitions = state.get_transitions()
        self.assertTrue(len(transitions) == 2)

    def test_s4_available_transitions(self):
        self.sm.set_state(2)
        self.sm.set_state(4)
        state = self.sm.get_state()
        transitions = state.get_transitions()
        self.assertTrue(len(transitions) == 1)
        labels = ", ".join([s._label for s in transitions])
        self.assertEqual(labels, "Resolve")


if __name__ == '__main__':
    unittest.main()
