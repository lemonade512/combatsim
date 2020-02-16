import pytest

from combatsim.event import EventLog


def test_event_log_tracks_encounter_round(encounter, event_log):
    encounter.combat_round=4
    assert event_log.log("Test").round == 4

def test_event_log_adds_new_events(event_log):
    event_log.log("Hello")
    assert event_log.events[0].message == "Hello"
