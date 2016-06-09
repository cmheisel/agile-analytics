from datetime import datetime


class AgileTicket(object):
    def __init__(self, key):
        self.key = str(key)
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

        try:
            datetime.now() - value['entered_at']
        except TypeError:
            entered_at = value['entered_at']
            msgvars = dict(
                val_type=type(entered_at),
                val=entered_at,
            )
            raise TypeError("Flow log items must have a entered_at datetime. Got: {val_type} / {val}".format(**msgvars))

        value[u'state'] = unicode(value['state'])
        super(FlowLog, self).append(value)
