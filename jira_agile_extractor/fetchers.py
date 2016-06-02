class BaseFetcher(object):
    def fetch():
        raise NotImplementedError

class JIRAFetcher(BaseFetcher):
    BASIC_AUTH_KEYS=['username', 'password']
    OAUTH_KEYS=['access_token', 'access_token_secret', 'consumer_key', 'key_cert']

    def __init__(self, auth, filter_id):
        self.auth = auth
        print self.auth.keys()
        self._validate_auth()
        self.filter_id = filter_id

    def _validate_auth(self):
        if set(self.auth.keys()) <= set(self.BASIC_AUTH_KEYS) and \
            set(self.auth.keys()) <= set(self.OAUTH_KEYS):
                raise TypeError("Neither %s nor %s found in auth parameter" % \
                    (self.BASIC_AUTH_KEYS, self.OAUTH_KEYS))
