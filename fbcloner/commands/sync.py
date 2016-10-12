from datetime import datetime
import facebook
import logging
import requests

_logger = logging.getLogger('fbcloner.sync')


class FbFeedIter(object):
    FB_API_VERSION = '2.7'
    ISO_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

    def __init__(self, access_token, fbid='me', since=None, until=None):
        """Constructor.

        :param str access_token: The access token.
        :param datetime since: The starting date of the date range.
        :param datetime until: The ending date of the date range.
        """
        self.access_token = access_token
        self.fbid = fbid
        self.since = since
        self.until = until
        self._next_page = None
        self._date = None
        self._post_iter = self._get_next_post_set()

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        try:
            post = next(self._post_iter)
            self._date = datetime.strptime(
                post['created_time'], self.ISO_DATE_FORMAT)
            return post
        except StopIteration:
            if self._date >= self.since:
                self._post_iter = self._get_next_post_set()
                return self.next()
            else:
                raise

    def _get_next_post_set(self):
        if self._next_page:
            feed = requests.get(self._next_page).json()
        else:
            graph = facebook.GraphAPI(
                access_token=self.access_token, version=self.FB_API_VERSION)
            feed = graph.get_connections(
                id=self.fbid,
                connection_name='feed',
                fields=(
                    'status_type,id,created_time,message,link,full_picture,'
                    'object_id'),
                since=self.since,
                until=self.until)

        self._next_page = feed.get('paging', {}).get('next')
        return iter(feed['data'])


def sync(conn_str, fbid, since, until):
    """
    Sync the Facebook feed.

    :param str conn_str: The connection string.
    :param str fbid: The Facebook ID.
    :param str since: The from date string.
    :param str until: The until date string.
    """
    access_token = open('.fbtoken').read()
    # TODO We would need extra code to check access token expiry

    post_iter = FbFeedIter(access_token, fbid, since, until)
    _logger.debug('Single post: {}'.format(post_iter.next()))
