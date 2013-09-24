#!/usr/bin/python
# -*- coding: utf8 -*-

import unittest
from ringo.model.statemachine import Statemachine, State, handler


class DummyItem(object):
    pass

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.s1 = State(1, "In Bearbeitung")
        self.s2 = State(2, "Eingereicht")
        self.s3 = State(3, "Validiert")

        self.s1.add_transition(self.s2, "Einreichen", handler)
        self.s2.add_transition(self.s3, "Prüfung Abschließen", handler)
        self.s3.add_transition(self.s2, "Erneut Prüfen", handler)
        self.s3.add_transition(self.s1, "Erneut Bearbeiten", handler)
        self.s2.add_transition(self.s1, "Erneut Bearbeiten", handler)

        self.sm = Statemachine(DummyItem(), self.s1)

    def test_num_states(self):
        self.assertTrue(len(self.sm.get_states()) == 3)

    def test_s12s2(self):
        state = self.sm.set_state(self.s2)
        self.assertEqual(state, self.s2)

    def test_s12s3(self):
        with self.assertRaises(Exception):
            self.sm.set_state(self.s3)

if __name__ == '__main__':
    unittest.main()
