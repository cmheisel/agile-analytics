from datetime import datetime


class AgileTicket(object):
    def __init__(self, key):
        self.key = unicode(key)
        self.created_at = None
        self.updated_at = None
        self._flow_log = FlowLog()

    @property
    def flow_log(self):
        return self._flow_log


class FlowLog(list):
    def append(self, value):
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
