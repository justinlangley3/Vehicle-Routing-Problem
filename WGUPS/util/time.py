import math
from datetime import time, datetime


def time_from_string(t: str) -> time | None:
    # split time passed in into tokens that can be processed individually
    def _tokenize(raw_time: str):
        _am_pm = raw_time.split(sep=' ')[1]
        raw_time = raw_time[0:-3]
        _h = raw_time.split(sep=':')[0]
        _m = raw_time.split(sep=':')[1]
        return int(_h), int(_m), _am_pm

    if t is None:
        return None

    # return default time for end of business day if 'EOD' is passed in
    if 'eod' in t.lower():
        return time(23, 59, 59, 999999)

    # tokenize time passed in and format to 24hr time format
    hours, minutes, am_pm = _tokenize(t)
    if 'pm' in am_pm.lower():
        hours += 12

    return time(hour=hours, minute=minutes)


def calc_travel_time(distance: float, rate: int):
    t = (distance / rate) * 3600  # time elapsed (in seconds)
    h = math.floor(t / 3600)  # hours
    m = math.floor(t % 3600 / 60)  # minutes
    s = math.floor(t % 3600 % 60)  # seconds
    return h, m, s


def to_digital_clock(d: datetime) -> str:
    """
    Method to form a digital clock representation of a time contained in a datetime
    Args:
        d: datetime

    Returns: str

    """
    hours = d.hour
    minutes = d.minute
    seconds = d.second
    am_pm = 'AM' if hours > 12 else 'PM'
    if hours > 12:
        hours -= 12
    return f'{hours}:{minutes}:{seconds} {am_pm}'
