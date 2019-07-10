import pytz
from datetime import datetime


def parse_unix_datetime(num):
    """
    Converts UNIX time from USGS to a localized datetime object.
    """
    naive_dt = datetime.utcfromtimestamp(num / 1000)
    return pytz.utc.localize(naive_dt)


default_app_config = 'anss.apps.AnssConfig'
