from datetime import datetime
import facebook
import json
import logging
import requests

_logger = logging.getLogger('fbcloner.sync')


class FbFeedIter(object):
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

        self._initialize_graph()

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
            if self._date >= self.since and self._next_page:
                feed = requests.get(self._next_page).json()
                self._generate_new_iter(feed)
                return self.next()
            else:
                raise

    def _initialize_graph(self):
        graph = facebook.GraphAPI(access_token=self.access_token)
        feed = graph.get_connections(
            id=self.fbid,
            connection_name='feed',
            fields=(
                'status_type,id,created_time,message,link,full_picture,'
                'object_id'),
            since=self.since,
            until=self.until)

        self._generate_new_iter(feed)

    def _generate_new_iter(self, feed):
        self._next_page = feed.get('paging', {}).get('next')
        self._post_iter = iter(feed['data'])


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
    counter = 1
    for post in post_iter:
        filename = 'feeddump/{}-{}.json'.format(
            post['created_time'], post['id'])

        with open(filename, 'w') as pfhdl:
            json.dump(post, pfhdl)

        if counter % 100 == 0:
            _logger.info('Processed {} posts - {}'.format(
                counter, post['created_time']))
        counter = counter + 1
