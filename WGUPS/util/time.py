import math
from copy import copy
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
        hours += 11
    else:
        if hours == 12:
            hours = 0

    return time(hour=hours, minute=minutes)


def datetime_from_string(t: str) -> datetime:
    """
    Handles making times internally, but this is also where times have to be validated,
    since any time the user enters will eventually be made into a datetime here

    Args:
        t: str

    Returns: datetime

    """
    # cleanup the time passed in,
    # so it doesn't break our simple time parsing techniques
    t = t.strip()
    t_copy = copy(t)
    am_pm = ''
    if ('am' or 'pm') in t_copy:
        am_pm = t_copy[len(t_copy) - 2: len(t_copy)]
        t_copy = t_copy[:-2].strip()
    if t_copy.count(':') > 1:
        t = t_copy[:-2] + ' ' + am_pm
    else:
        t = t_copy + ' ' + am_pm

    today = datetime.today()
    parsed = time_from_string(t)
    return datetime(today.year, today.month, today.day, parsed.hour, parsed.minute, 0, 0)


# noinspection PyUnusedLocal
def calc_travel_time(distance: float, rate: int):
    """Compute timedelta (in microseconds) of the time it takes to travel a distance at a given rate"""
    from datetime import timedelta
    if distance is None:
        return timedelta(microseconds=0)
    unit = 3600 * 1000
    t = (distance / rate) * unit
    h = math.floor(t / 1000 / 60 / 60) % 24
    m = math.floor(t / 1000 / 60 % 60)
    s = math.floor(t / 1000 % 60)
    ms = math.floor(t % 3600 % 1000)
    return timedelta(hours=h, minutes=m, seconds=s)


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
    am_pm = 'AM' if hours < 12 else 'PM'
    hours -= 0 if hours < 12 else 12
    hours = str(hours) if hours > 9 else '0' + str(hours)
    minutes = str(minutes) if minutes > 9 else '0' + str(minutes)
    seconds = str(seconds) if seconds > 9 else '0' + str(seconds)

    return f'{hours}:{minutes}:{seconds} {am_pm}'
