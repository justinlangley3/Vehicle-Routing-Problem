# STL Imports
from re import compile, match

# Project Imports


def is_time_valid(t: str) -> bool:
    # match 24hr time format
    pattern = compile('^([01]?[0-9]|2[0-3]):([0-5][0-9])$')
    if match(pattern, t):
        return True
    return False
