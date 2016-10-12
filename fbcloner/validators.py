import dateutil.parser as dtparser
from datetime import timezone


def validate_datetime(value):
    """
    Validate the date time.

    :param str value: The data value as a date time string.
    :returns: The converted date time.
    :rtype: datetime
    """
    return dtparser.parse(value).replace(tzinfo=timezone.utc)
