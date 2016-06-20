"""Data models."""

from datetime import datetime


class AgileTicket(object):
    """Abstract representation of tickets in Agile systems.

    Attributes:
        key (unicode): Unique identifier for the ticket in its system of record
        created_at (datetime): When was the ticket created
        updated_at (datetime): When was the ticket last updated
    """

    def __init__(self, key):
        """Init an AgileTicket.

        Args:
            key (str): A unique identifier for this ticket in the system of record
        """
        self.key = unicode(key)
        self.created_at = None
        self.updated_at = None
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
                exc=unicode(e)
            )
            raise TypeError("Flow log items must have a entered_at datetime. Got: {val_type} / {val}, \n Exception: {exc}".format(**msgvars))

        value[u'state'] = unicode(value['state'])
        super(FlowLog, self).append(value)
        super(FlowLog, self).sort(key=lambda x: x['entered_at'])


class AnalyzedAgileTicket(object):
    """An AgileTicket analyzed within a certain context.

    Attributes:
        key (unicode): Unique identifier for the ticket in its system of record
        committed (dict): The state and datetime when the story was committed
        started (dict): The state and datetime when the story was started
        ended (dict): The state and datetime when the story was ended

    Optional Attributes:
        type (unicode): A label of the type of ticket: Story, Epic, Defect
    """

    def __init__(
        self, key, committed, started, ended,
        type="Ticket",
    ):
        """Create AnalyzedAgileTickets."""
        self.key = key
        self.committed = committed
        self.started = started
        self.ended = ended
