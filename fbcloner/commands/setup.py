from facebook import GraphAPI
import logging

_logger = logging.getLogger('fbcloner.setup')


def setup():
    """
    Setup the Facebook Cloner.
    """
    client_id = input('Enter the Facebook client ID: ')
    client_secret = input('Enter the Facebook client secret: ')
    code = input('Enter the OAuth2 code: ')
    redirect_uri = input('Enter the redirect URI: ')

    graph = GraphAPI()
    access_token = graph.get_access_token_from_code(
        code, redirect_uri, client_id, client_secret)['access_token']

    _logger.debug(access_token)
    with open('.fbtoken', 'w') as token_file:
        token_file.write(access_token)

    _logger.info('App access token saved')
