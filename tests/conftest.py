import pytest

from combatsim.creature import Monster
from combatsim.encounter import Encounter
from combatsim.event import EventLog


@pytest.fixture
def encounter():
    return Encounter([])

@pytest.fixture
def event_log(encounter):
    return EventLog(encounter)

@pytest.fixture
def monster():
    return Monster()
