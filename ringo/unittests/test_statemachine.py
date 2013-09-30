#!/usr/bin/python
# -*- coding: utf8 -*-

import unittest
from ringo.model.statemachine import Statemachine, State, \
    null_handler as handler


class DummyItem(object):
    pass


class DummyStatemachine(Statemachine):

    def setup(self):
        s1 = State(1, "Unconfirmed")
        s2 = State(2, "New")
        s3 = State(3, "Reopend")
        s4 = State(4, "Assigned")
        s5 = State(5, "Resolved")
        s6 = State(6, "Verfified")
        s7 = State(7, "Closed")

        s1.add_transition(s5, "Decline", handler)
        s1.add_transition(s2, "Accept", handler)

        s2.add_transition(s4, "Assign", handler)
        s3.add_transition(s4, "Reassign", handler)

        s4.add_transition(s5, "Resolve", handler)

        s5.add_transition(s4, "Revise", handler)
        s5.add_transition(s6, "Verify", handler)

        s6.add_transition(s7, "Close", handler)
        s6.add_transition(s5, "Reopen", handler)

        s7.add_transition(s3, "Reopen", handler)
        return s1


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.sm = DummyStatemachine(DummyItem())

    def test_num_states(self):
        self.assertTrue(len(self.sm.get_states()) == 7)

    def test_s12s2(self):
        state = self.sm.set_state(2)
        self.assertEqual(state._id, 2)

    def test_s1s3(self):
        with self.assertRaises(Exception):
            self.sm.set_state(3)

    def test_start_state(self):
        self.sm = DummyStatemachine(DummyItem(), 2)
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
