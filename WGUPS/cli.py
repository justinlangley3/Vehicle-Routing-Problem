# STL
import copy
import csv
import glob
import os
import pathlib
import re
import sys
import time
from collections import ChainMap

import util
from globals import Colors


def cmd_help(arg: str):
    text = ''
    match arg:
        case 'l':
            text = f'Usage:\n' \
                   f'-l [option] [value]\n' \
                   f'-------------------' \
                   f'Option\t|\tValue\n' \
                   f'--------------------\n' \
                   f'a, lookup package by ADDRESS\n' \
                   f'd, lookup package by DEADLINE\n' \
                   f'c, lookup package by CITY\n' \
                   f'i, lookup package by ID\n' \
                   f's, lookup package by STATUS\n' \
                   f'w, lookup package by WEIGHT\n' \
                   f'z, lookup package by ZIP'
        case 'la':
            text = f'Usage:\n' \
                   f'-la [value], lookup package by ADDRESS\n' \
                   f'Description:\n' \
                   f'The value parameter must exactly match the street address of the package.'
        case 'ld':
            text = f'Usage:\n' \
                   f'-ld [value], lookup package by DEADLINE\n' \
                   f'Description:\n' \
                   f'The value must be a valid time in 24hr format [HH:MM] e.g. 09:59 or 21:59.'
        case 'lc':
            text = f'Usage:\n' \
                   f'-lc [value], lookup package by CITY\n' \
                   f'Description:\n' \
                   f'The value must exactly match the city of the package.'
        case 'li':
            text = f'Usage:\n' \
                   f'-li [value], lookup package by ID\n' \
                   f'Description:\n' \
                   f'The value must be a valid integer ID of the package.'
        case 'ls':
            text = f'Usage:\n' \
                   f'-ls [value], lookup package by STATUS\n' \
                   f'Description:\n' \
                   f'The value must match a valid status: \'hub\', \'enroute\', \'delivered\'.'
        case 'lw':
            text = f'Usage:\n' \
                   f'-lw [value], lookup package by WEIGHT\n' \
                   f'Description:\n' \
                   f'The value must be a valid integer value.'
        case 'lz':
            text = f'Usage:\n' \
                   f'-lz [value], lookup package by ZIP\n' \
                   f'Description:\n' \
                   f'The value must be a valid 5-digit zipcode.'
        case 's':
            text = f'Usage:\n' \
                   f'-s[option], simulate delivery of currently loaded trucks' \
                   f'Description:\n' \
                   f'Simulates delivery using the specified algorithm option.\n' \
                   f'If no option is chosen, convex hull is used by default.' \
                   f'Options:\n' \
                   f'a - ant colony optimization (metaheuristic)\n' \
                   f'c - convex hull\n' \
                   f'g - genetic algorithm (metaheuristic)\n' \
                   f'n - nearest neighbor'
        case 'm':
            text = f'Usage:\n' \
                   f'-m' \
                   f'Description:' \
                   f'Displays metrics of any present trucks if delivery has been simulated.'
        case 'u':
            text = f'Usage:\n' \
                   f'-u[option] [value]\n' \
                   f'Description:\n' \
                   f'Update a package parameter to the specified value.\n' \
                   f'Options:\n' \
                   f'a, address\n' \
                   f'd, deadline\n' \
                   f'c, city\n' \
                   f'w, weight\n' \
                   f'z, zip'
        case '_':
            text = 'Invalid argument provided'
    print(text)


def ls(path: str, ext: str = '') -> list[pathlib.Path]:
    """
    Returns a list of files with the specified extension in a directory
    Orders files by most recently modified -> least recently modified
    """
    files = sorted(glob.glob(path + '*' + ext), key=os.path.getmtime, reverse=True)
    paths = [pathlib.Path(f).resolve() for f in files]
    return paths


def file_choose(files: list[pathlib.Path]) -> pathlib.Path:
    """
    Presents a small subset of files to the user, and returns their selection

    Example Output:
    Please select a file:
    #    |    Name    |    Date
    ---------------------------
    0):  example.ext    2022-01-01
    > _
    """
    files_as_str = ""
    f = files[:10] if len(files) > 9 else copy.copy(files)
    for index, value in enumerate(f):
        file = f'{Colors.GREEN1}' \
               f'    {index}):\t' \
               f'{Colors.BLUE2}    ' \
               f'  {value.stem}{value.suffix}\t\t' \
               f'{Colors.YELLOW2}' \
               f' {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(value)))}' \
               f'{Colors.END}\n'
        files_as_str = files_as_str.join(file)
    files_as_str += f'{Colors.GREEN1}>{Colors.END} '

    prompt = f'{Colors.RED1}Please select a file:{Colors.END}\n' \
             f'{Colors.GREY}------------------------------------------------------------{Colors.END}\n' \
             f'{Colors.BOLD}|   #  \t|\t  Name\t\t\t|\tDate\t   |\n{Colors.END}' \
             f'{Colors.GREY}------------------------------------------------------------{Colors.END}\n' \
             f'{files_as_str}'
    pattern = re.compile("^[0-9]$")

    is_file_selected = False
    while not(is_file_selected):
        cls()
        choice = input(prompt)
        try:
            assert re.match(pattern, choice)
            assert 0 <= int(choice) < len(f)
            is_file_selected = True
            return f[int(choice)]
        except AssertionError:
            print(f'{Colors.RED1}Input must be a value shown{Colors.END}', flush=True)
            input(f'Press {Colors.YELLOW2}ENTER{Colors.END} to retry ...')
            pass


def is_time_valid(t: str) -> bool:
    # match 24hr time format
    pattern = re.compile('^([01]?[0-9]|2[0-3]):([0-5][0-9])$')
    if re.match(pattern, t):
        return True
    return False


def cls():
    print("\033[H\033[J", end="", flush=True)


def progress(steps, prefix: str = "", size: int = 60, file=sys.stdout) -> None:
    count = len(steps)

    def show(j):
        x = int(size * j / count)
        file.write("{}[{}{}] {}%/{}%\r".format(prefix, "#" * x, "." * (size - x), j, count))
        file.flush()
        show(0)

    for i, item in enumerate(steps):
        yield item
        show(i + 1)
    file.write("\n")
    file.flush()


def argparse(args: str):
    """
    """
    def make_kvpair(t: str, sep: str) -> dict[str, str]:
        items = t.split(sep=sep)
        pair = dict()
        pair[items[0]] = items[1]
        return pair

    def splitchars(s: str):
        return list[s]

    def tokenize(raw: str):
        t = raw.split(sep=' ')
        d = ChainMap()
        d['keys'] = None
        for i, item in enumerate(t):
            d[i] = item
        return d

    tokens = tokenize(args)

    return tokens
