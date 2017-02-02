"""Data models."""

from datetime import datetime


class AgileTicket(object):
    """Abstract representation of tickets in Agile systems.

    Attributes:
        key (unicode): Unique identifier for the ticket in its system of record
        created_at (datetime): When was the ticket created
        updated_at (datetime): When was the ticket last updated
        type (str): The kind of ticket this is: Bug, Epic, Story, etc.

    Optional Attributes:
        title (unicode): The title of the ticket
        type (unicode): A label of the type of ticket: Story, Epic, Defect
    """

    def __init__(self, key, title="", ttype="Ticket"):
        """Init an AgileTicket.

        Args:
            key (str): A unique identifier for this ticket in the system of record
        """
        self.key = str(key)
        self.title = title
        self.created_at = None
        self.updated_at = None
        self.type = ttype
        self._flow_log = FlowLog()

    @property
    def flow_log(self):
        """FlowLog[dict].

        A list of dicts guaranteed to have the following:
            entered_at (datetime): When the ticket entered the state
            state (unicode): The name of the state the ticket entered
        """
        return self._flow_log


class FlowLog(list):
    """List subclass enforcing dictionaries with specific keys are added to it."""

    def append(self, value):
        """Add items to the list.

        Args:
            value (dict): Must contain an entered_at and state key.

        Returns:
            None

        Raises:
            TypeError: Flow log items must have a 'entered_at' datetime and a 'state' string.
        """
        try:
            ('entered_at', 'state') in value.keys()
        except AttributeError:
            raise TypeError("Flow log items must have a 'entered_at' datetime and a 'state' string. Got: {value}".format(value=value))

        entered_at = value['entered_at']
        try:
            datetime.now(entered_at.tzinfo) - entered_at
        except (AttributeError, TypeError) as e:
            msgvars = dict(
                val_type=type(entered_at),
                val=entered_at,
                exc=str(e)
            )
            raise TypeError("Flow log items must have a entered_at datetime. Got: {val_type} / {val}, \n Exception: {exc}".format(**msgvars))

        value[u'state'] = str(value['state'])
        super(FlowLog, self).append(value)
        self.sort(key=lambda l: l['entered_at'])


class AnalyzedAgileTicket(object):
    """An AgileTicket analyzed within a certain context.

    Attributes:
        key (unicode): Unique identifier for the ticket in its system of record
        committed (dict): The state and datetime when the story was committed
        started (dict): The state and datetime when the story was started
        ended (dict): The state and datetime when the story was ended

    Optional Attributes:
        title (unicode): The title of the ticket
        type (unicode): A label of the type of ticket: Story, Epic, Defect
    """

    def __init__(
        self, key, committed, started, ended,
        title="", ttype="Ticket",
    ):
        """Create AnalyzedAgileTickets."""
        self.key = key
        self.title = title
        self.committed = committed
        self.started = started
        self.ended = ended
        self.type = ttype

    def __repr__(self):
        """Represention of the object."""
        return "{} -- Ended: {}".format(self.key, self.ended['entered_at'])

    @property
    def lead_time(self):
        """Number of days between committed and ended."""
        diff = self.ended['entered_at'] - self.committed['entered_at']
        return diff.days

    @property
    def cycle_time(self):
        """Number of days between started and ended."""
        diff = self.ended['entered_at'] - self.started['entered_at']
        return diff.days
