import getpass
import facebook
import json
import requests
from datetime import datetime, timezone
from elasticsearch import Elasticsearch

FB_API_VERSION = '2.5'
ISO_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
ES_INDEX = 'felix_fbfeed'

es = Elasticsearch()

access_token = getpass.getpass('Access token:')
continue_parse = True
date = None
next_page = None
while continue_parse:
    if next_page:
        feed = requests.get(next_page).json()
    else:
        graph = facebook.GraphAPI(
            access_token=access_token, version=FB_API_VERSION)
        feed = graph.get_connections(
            id='me',
            connection_name='posts',
            fields='status_type,id,created_time,message,link')

    paging = feed['paging']
    post_set = feed['data']

    for post in post_set:
        date = datetime.strptime(post['created_time'], ISO_DATE_FORMAT)

        es.index(
            index=ES_INDEX,
            doc_type=post.get('status_type', 'mobile_status_update'),
            id=post['id'],
            body=post)

    next_page = paging.get('next')
    continue_parse = (
        date >= datetime(2014, 9, 1, tzinfo=timezone.utc) and
        next_page is not None)
