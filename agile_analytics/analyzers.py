"""Analyzers decorate AgileTickets with contextual information.

Analyzers look at tickets through the lens of "this is my start state", or
"this is what defects look like" and modify AgileTickets to contain information
based on that context like "ended_at", "commited_at", "started_at", etc.
"""

from .models import AnalyzedAgileTicket


class MissingPhaseInformation(Exception):
    """Raise when a ticket is missing information for a phase.

    Arguments:
        message (unicode): Human readable string describing the exception.
        phase (unicode): The phase that no state could be found for.
        state_list (list[unicode]): List of states that were included in the phase.

    Attritbutes:
        message (unicode): Human readable string describing the exception.
        phase (unicode): The phase that no state could be found for.
        state_list (list[unicode]): List of states that were included in the phase.
    """

    def __init__(self, message, phase, state_list):
        """Create the exception."""
        self.message = message
        self.phase = phase
        self.state_list = state_list
        super(Exception, self).__init__(message)


class PartialDateAnalyzer(object):
    """Analyze Tickets that might not have been started or completed.

    Attributes:
        commit_state (list[str]): The list of names of the state when work was committed to.
        start_state (list[str]): The list of names of the state when work was started.
        end_state (list[str]): The list of names of the state when work was completed.
    """
    def __init__(self, commit_states, start_states, end_states):
        """Create instances."""
        self.end_states = end_states
        self.commit_states = commit_states
        self.start_states = start_states
        super().__init__()

    @property
    def states_context(self):
        """Enumerate the states that match the phases of an analyzed ticket."""
        return {
            u'committed': self.commit_states,
            u'started': self.start_states,
            u'ended': self.end_states,
        }

    def _find_entered_at(self, state_list, ticket, dupe_strategy="oldest"):
        entry = dict(state=None, entered_at=None)
        entries = []
        for state_name in state_list:
            for log in ticket.flow_log:
                if log['state'] == state_name:
                    entries.append(log)
            if len(entries) > 0:
                break

        if len(entries) > 0:
            if dupe_strategy == "oldest":
                entry = entries[0]
            else:
                entry = entries[-1]
        return entry['state'], entry['entered_at']

    def analyze(self, tickets):
        """Return a list of AnalyzedAgileTicket.

        Arguments:
            tickets (list[AgileTicket]): The list of tickets to be analyzed

        Returns:
            list[AnalyzedAgileTicket]: The list of tickets
        """
        analyzed_tickets = []
        ignored_tickets = []
        for ticket in tickets:
            analyzed_tickets.append(self.analyze_ticket(ticket))
        return analyzed_tickets, ignored_tickets

    def analyze_ticket(self, ticket):
        """Convert a single AgileTicket into an AnalyzedAgileTicket.

        Arguments:
            ticket (AgileTicket): The AgileTicket under consideration

        Returns:
            AnalyzedAgileTicket
        """
        kwargs = {
            "key": ticket.key,
            "ttype": ticket.type,
            "title": ticket.title,
        }

        for phase, state_list in self.states_context.items():
            dupe_strategy = "oldest"
            if phase == "ended":
                dupe_strategy = "newest"
            state, datetime = self._find_entered_at(state_list, ticket, dupe_strategy=dupe_strategy)
            kwargs[phase] = dict(state=state, entered_at=datetime)
        return AnalyzedAgileTicket(**kwargs)


class DateAnalyzer(PartialDateAnalyzer):
    """Analyze Tickets for cycle data.

    Attributes:
        commit_state (list[str]): The list of names of the state when work was committed to.
        start_state (list[str]): The list of names of the state when work was started.
        end_state (list[str]): The list of names of the state when work was completed.
    """

    def analyze(self, tickets):
        """Return a list of AnalyzedAgileTicket.

        Arguments:
            tickets (list[AgileTicket]): The list of tickets to be analyzed

        Returns:
            list[AnalyzedAgileTicket]: The list of tickets
        """
        analyzed_tickets = []
        ignored_tickets = []
        for ticket in tickets:
            try:
                analyzed_tickets.append(self.analyze_ticket(ticket))
            except MissingPhaseInformation as e:
                ignored_tickets.append(dict(ticket=ticket, phase=e.phase, state_list=e.state_list))
        return analyzed_tickets, ignored_tickets

    def analyze_ticket(self, ticket):
        """Convert a single AgileTicket into an AnalyzedAgileTicket.

        Arguments:
            ticket (AgileTicket): The AgileTicket under consideration

        Returns:
            AnalyzedAgileTicket
        """
        kwargs = {
            "key": ticket.key,
            "ttype": ticket.type,
            "title": ticket.title,
        }

        for phase, state_list in self.states_context.items():
            dupe_strategy = "oldest"
            if phase == "ended":
                dupe_strategy = "newest"
            state, datetime = self._find_entered_at(state_list, ticket, dupe_strategy=dupe_strategy)
            if None in (state, datetime):
                msg = "{key} is missing flow_log information for {state_list}".format(key=ticket.key, state_list=state_list)
                raise MissingPhaseInformation(
                    msg,
                    phase,
                    state_list,
                )
            kwargs[phase] = dict(state=state, entered_at=datetime)
        return AnalyzedAgileTicket(**kwargs)
