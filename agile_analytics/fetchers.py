"""Fetch data from agile sources and return standard AgileTickets."""

from dateutil.parser import parse
from jira import JIRA

from .models import AgileTicket


class BaseFetcher(object):
    """Base class for Fetchers."""

    def fetch():
        """Method invoked to fetch.

        Args:
            None
        Returns:
            None
        Raises:
            NotImplementedError
        """
        raise NotImplementedError  # pragma: no cover


def convert_jira_issue(issue):
    """
    Convert a JIRA issue into a AgileTicket.

    Args:
        issue (Issue): A jira.Issue instance

    Returns:
        An AgileTicket instance

    Raises:
        None
    """
    try:
        ttype = issue.fields.issuetype.name
    except AttributeError:
        ttype = "Ticket"

    t = AgileTicket(issue.key, ttype=ttype)

    t.title = issue.fields.summary
    t.created_at = parse(issue.fields.created)
    t.updated_at = parse(issue.fields.updated)
    t.flow_log.append(
        dict(
            entered_at=t.created_at,
            state=str("Created"),
        )
    )

    for history in issue.changelog.histories:
        for item in history.items:
            if item.field == 'status':
                t.flow_log.append(
                    dict(
                        entered_at=parse(history.created),
                        state=str(item.toString)
                    )
                )

    return t


class JIRAFetcher(BaseFetcher):
    """Fetch data from JIRA and transform it into AgileTickets.

    Attributes:
        jira_kwargs (dict): The arguments passed to the JIRA instance.
        auth_kwargs (dict): The authentication kwargs passed to the JIRA instance
    """

    BASIC_AUTH_KEYS = ['username', 'password']
    OAUTH_KEYS = ['access_token', 'access_token_secret', 'consumer_key', 'key_cert']

    def __init__(self, url, auth, filter_id, max_results=999, jira_kwargs=None):
        """Create JIRAFetcher.

        Args:
            url (str): Fully qualified URL include http/https scheme to your JIRA instance
            auth (dict): Dictionary of authentication credentials. Either username/password keys
                for basic auth OR access_token/access_token_secret/consumer_key/key_cert for OAuth
            filter_id (int): The JIRA filter ID of results you wish to fetch
            max_results (Optional[int]): Number of results to fetch, defaults to 999
            jira_kwargs (Optional[dict]): Additional kwargs passed to the jira.JIRA class
                at instance creation

        Returns:
            JIRAFetcher: instance

        Raises:
            TypeError: When neither Basic nor Oauth keys were provided in the auth dict
        """
        self._url = url
        self._auth = auth
        self.auth_kwargs = {}
        self._validate_auth()
        self._filter_id = int(filter_id)
        self.jira_kwargs = jira_kwargs or {}
        self.jira_kwargs.update(self.auth_kwargs)
        self._max_results = max_results

    def _validate_auth(self):
        if set(self._auth.keys()) <= set(self.BASIC_AUTH_KEYS):
            self.auth_kwargs = dict(basic_auth=(self._auth['username'], self._auth['password']))
        elif set(self._auth.keys()) <= set(self.OAUTH_KEYS):
            self.auth_kwargs = dict(oauth=self._auth)
        else:
            raise TypeError("Neither %s nor %s found in auth parameter" % (self.BASIC_AUTH_KEYS, self.OAUTH_KEYS))

    # TODO: Needs tests
    def fetch(self, jira_klass=JIRA):
        """Fetch data and return AgileTickets.

        Args:
            jira_klass (Optional[JIRA]): jira.JIRA compatible class to be used for a JIRA connection

        Returns:
            list: List of AgileTicket instances or empty list

        Raises:
            None
        """
        j = jira_klass(
            server=self._url,
            **self.jira_kwargs
        )
        search_string = "filter={filter_id}".format(filter_id=self._filter_id)
        issues = j.search_issues(search_string, maxResults=self._max_results, expand="changelog")
        tickets = []
        for i in issues:
            tickets.append(convert_jira_issue(i))
        return tickets
