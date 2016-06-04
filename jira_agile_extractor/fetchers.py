from jira import JIRA


class BaseFetcher(object):
    def fetch():
        raise NotImplementedError


class JIRAFetcher(BaseFetcher):
    BASIC_AUTH_KEYS = ['username', 'password']
    OAUTH_KEYS = ['access_token', 'access_token_secret', 'consumer_key', 'key_cert']

    def __init__(self, url, auth, filter_id, jira_kwargs=None):
        self.url = url
        self.auth = auth
        self.auth_kwargs = {}
        self._validate_auth()
        self.filter_id = int(filter_id)
        self.jira_kwargs = jira_kwargs or {}
        self.jira_kwargs.update(self.auth_kwargs)

    def _validate_auth(self):
        if set(self.auth.keys()) <= set(self.BASIC_AUTH_KEYS) and set(self.auth.keys()) <= set(self.OAUTH_KEYS):
            raise TypeError("Neither %s nor %s found in auth parameter" % (self.BASIC_AUTH_KEYS, self.OAUTH_KEYS))
        if set(self.auth.keys()) <= set(self.BASIC_AUTH_KEYS):
            self.auth_kwargs = dict(basic_auth=(self.auth['username'], self.auth['password']))
        elif set(self.auth.keys()) <= set(self.OAUTH_KEYS):
            self.auth_kwargs = dict(oauth=self.auth)
        else:
            raise TypeError("Neither %s nor %s found in auth parameter" % (self.BASIC_AUTH_KEYS, self.OAUTH_KEYS))

    def fetch(self):
        j = JIRA(server=self.url,
                 **self.jira_kwargs)
        assert j
