class BaseFetcher(object):
    def fetch():
        raise NotImplementedError

class JIRAFetcher(BaseFetcher):
    def __init__(self, auth, filter_id):
        self.auth = auth
        self.filter_id = filter_id
