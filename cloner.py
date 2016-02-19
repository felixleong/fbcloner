"""
Facebook feed cloner.

Usage:
    cloner.py [--from=<date>] [--until=<date>] [--fbid=<fbid>] <es_index>

Options:
    <es_index>      The Elastic Search index, either the full URL or the
                    index name on localhost.
    --from=<date>   The starting bound of the date range.
    --until=<date>  The ending bound of the date range.
    --fbid=<fbid>   The Facebook ID to clone the data from [default: me].
"""
import getpass
import facebook
import requests
import dateutil.parser as dtparser
from datetime import datetime, timezone
from docopt import docopt
from elasticsearch import Elasticsearch

ES_INDEX = 'felix_fbfeed'


class FbFeedIter(object):
    FB_API_VERSION = '2.5'
    ISO_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

    def __init__(self, access_token, from_date=None, until_date=None):
        """Constructor.

        :param str access_token: The access token.
        :param datetime from_date: The starting date of the date range.
        :param datetime until_date: The ending date of the date range.
        """
        self.access_token = access_token
        self.from_date = from_date
        self.until_date = until_date
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
            if self._date >= self.from_date:
                self._post_iter = self._get_next_post_set()
                return self.next()
            else:
                raise

    def _get_next_post_set(self):
        if self._next_page:
            feed = requests.get(self._next_page).json()
        else:
            graph = facebook.GraphAPI(
                access_token=access_token, version=self.FB_API_VERSION)
            feed = graph.get_connections(
                id='me',
                connection_name='posts',
                fields='status_type,id,created_time,message,link',
                since=self.from_date,
                until=self.until_date)

        self._next_page = feed.get('paging', {}).get('next')
        return iter(feed['data'])


if __name__ == '__main__':
    arguments = docopt(__doc__)

    # Parse all the arguments
    from_date = arguments['--from']
    if from_date is not None:
        from_date = dtparser.parse(from_date).replace(tzinfo=timezone.utc)
    else:
        from_date = datetime(1, 1, 1, 0, 0, tzinfo=timezone.utc)

    until_date = arguments['--until']
    if until_date is not None:
        until_date = (
            dtparser.parse(until_date).replace(tzinfo=timezone.utc))
    es_index = arguments['<es_index>']

    # Gain the access token and process
    access_token = getpass.getpass('Access token:')
    post_iter = FbFeedIter(access_token, from_date, until_date)

    es = Elasticsearch()
    for post in post_iter:
        es.index(
            index=es_index,
            doc_type=post.get('status_type', 'mobile_status_update'),
            id=post['id'],
            body=post)
