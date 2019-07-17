""" Code to handle keeping a log of events during an encounter. """

class EventLog:
    __singleton = None

    def __new__(cls, *args, **kwargs):
        if not cls.__singleton:
            cls.__singleton = super(EventLog, cls).__new__(cls)

        return cls.__singleton

    def __init__(self, encounter=None):
        self.encounter = encounter
        self.events = []

    def log(self, message):
        """ Logs a message in the event log """
        if not self.encounter:
            raise ValueError("EventLog encounter has not yet been initialized")

        new_event = Event(self.encounter.combat_round, message)
        self.events.append(new_event)
        return new_event


class Event:

    def __init__(self, round_, message):
        self.round = round_
        self.message = message
