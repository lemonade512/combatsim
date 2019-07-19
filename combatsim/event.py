""" Code to handle keeping a log of events during an encounter. """

class EventLog:
    """ The event log is a singleton that tracks events in encounters.

    Anytime a new encounter is started, it will start adding entries to the
    event log. Then, the event log can be used to perform basic statistical
    analysis or display what happened to the user.
    """
    __singleton = None

    def __new__(cls, *args, **kwargs):
        if not cls.__singleton:
            cls.__singleton = super(EventLog, cls).__new__(cls)

        return cls.__singleton

    def __init__(self, encounter=None):
        self.encounter = encounter
        self.events = []

    def __str__(self):
        output = ""
        for event in self.events:
            output += str(event) + "\n"
        return output

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

    def __str__(self):
        return f"{self.round}:: {self.message}"
