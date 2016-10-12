"""
Facebook feed cloner.

Usage:
    cloner.py setup [--debug]
    cloner.py sync [--since=<date>] [--until=<date>] [--fbid=<fbid>] [--debug] <conn_str>

Options:
    <conn_str>      Connection string.
    --since=<date>   The starting bound of the date range.
    --until=<date>  The ending bound of the date range.
    --fbid=<fbid>   The Facebook ID to clone the data from [default: me].
    --debug         Show debug information
"""
from datetime import datetime, timezone
from docopt import docopt
from fbcloner.commands import setup, sync
from fbcloner.validators import validate_datetime
from voluptuous import (
    Any, Coerce, Schema, Url)
import logging


__SYNC_SCHEMA = Schema({
    'setup': bool,
    'sync': bool,
    '--since': Any(None, validate_datetime),
    '--until': Any(None, validate_datetime),
    '--fbid': Any('me', Coerce(int)),
    '<conn_str>': Url(),
    '--debug': bool,
})


# Main line
if __name__ == '__main__':
    # Parse the arguments and run commands
    arguments = docopt(__doc__, version='Facebook Feed Cloner 0.1')
    if arguments['--since'] is None:
        arguments['--since'] = datetime(1, 1, 1, tzinfo=timezone.utc)

    # Set up our logger
    _logger = logging.getLogger('fbcloner')
    if arguments['--debug']:
        logging.basicConfig(level=logging.DEBUG)
        _logger.debug('Enable debug logging mode')
    else:
        logging.basicConfig(level=logging.INFO)

    logging.debug('Parsed arguments: {}'. format(arguments))

    # Run our commands
    if arguments['setup']:
        setup()
    elif arguments['sync']:
        arguments = __SYNC_SCHEMA(arguments)
        sync(
            arguments['<conn_str>'],
            arguments['--fbid'],
            arguments['--since'],
            arguments['--until'])
