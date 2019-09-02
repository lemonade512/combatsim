import unittest

from combatsim.encounter import Encounter
from combatsim.event import EventLog


class TestEventLog(unittest.TestCase):

    def setUp(self):
        self.test_encounter = Encounter([])

    def test_event_log_tracks_encounter_round(self):
        event_log = EventLog(self.test_encounter)
        self.test_encounter.combat_round=4
        self.assertEqual(event_log.log("Test").round, 4)

    def test_event_log_adds_new_events(self):
        event_log = EventLog(self.test_encounter)
        event_log.log("Hello")
        self.assertEqual(event_log.events[0].message, "Hello")

    def test_event_log_is_singleton(self):
        log = EventLog()
        log2 = EventLog()
        self.assertIs(log, log2)
