""" Code to handle keeping a log of events during an encounter. """

class EventLog:
    """ The event log is a singleton that tracks events in encounters.

    Anytime a new encounter is started, it will start adding entries to the
    event log. Then, the event log can be used to perform basic statistical
    analysis or display what happened to the user.
    """
    encounter = None
    events = []

    def __init__(self, encounter=None):
        EventLog.encounter = encounter
        EventLog.events = []
        EventLog.__singleton = self

    def __str__(self):
        """ Representation of events in the event log. """
        output = ""
        for event in EventLog.events:
            output += str(event) + "\n"
        return output

    @staticmethod
    def log(message):
        """ Logs a message in the event log """
        if not EventLog.encounter:
            return

        new_event = Event(EventLog.encounter.combat_round, message)
        EventLog.events.append(new_event)
        return new_event


class Event:

    def __init__(self, round_, message):
        self.round = round_
        self.message = message

    def __str__(self):
        return f"{self.round}:: {self.message}"
