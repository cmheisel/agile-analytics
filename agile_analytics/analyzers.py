"""Analyzers decorate AgileTickets with contextual information.

Analyzers look at tickets through the lens of "this is my start state", or
"this is what defects look like" and modify AgileTickets to contain information
based on that context like "ended_at", "commited_at", "started_at", etc.
"""

from .models import AnalyzedAgileTicket


class MissingPhaseInformation(Exception):
    def __init__(self, message, phase, state_list):
        self.message = message
        self.phase = phase
        self.state_list = state_list
        super(Exception, self).__init__(message)


class DateAnalyzer(object):
    """Analyze Tickets for cycle data.

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
        super(DateAnalyzer, self).__init__()

    @property
    def states_context(self):
        """Enumerate the states that match the phases of an analyzed ticket."""
        return {
            u'committed': self.commit_states,
            u'started': self.start_states,
            u'ended': self.end_states,
        }

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
        }

        for phase, state_list in self.states_context.items():
            state, datetime = self._find_entered_at(state_list, ticket)
            if None in (state, datetime):
                msg = "{key} is missing flow_log information for {state_list}".format(key=ticket.key, state_list=state_list)
                raise MissingPhaseInformation(
                    msg,
                    phase,
                    state_list,
                )
            kwargs[phase] = dict(state=state, entered_at=datetime)
        return AnalyzedAgileTicket(**kwargs)

    def _find_entered_at(self, state_list, ticket):
        for i in ticket.flow_log:
            if i['state'] in state_list:
                return i['state'], i['entered_at']
        return None, None
