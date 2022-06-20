from datetime import datetime

import pytz


def parse_unix_datetime(num):
    """
    Converts UNIX time from USGS to a localized datetime object.
    """
    naive_dt = datetime.utcfromtimestamp(num / 1000)
    return pytz.utc.localize(naive_dt)


default_app_config = "anss.apps.AnssConfig"
