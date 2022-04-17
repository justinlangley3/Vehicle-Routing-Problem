# STL
import operator
import os
import re
import signal
import sys

# Project imports
from .core.hub import Hub
from .cli.environment import get_platform
from .cli.style import Style
from .models import Package
from .util.time import datetime_from_string


# noinspection PyUnusedLocal
def _signal_handler(sig, frame):
    """Signal handler to exit gracefully on interrupt"""
    print("\nExiting ...")
    sys.exit(0)


def kill() -> None:
    """Sends a signal to halt the program"""
    if 'win' in get_platform():
        # OS is windows, send ctrl-c
        signal.raise_signal(signal.CTRL_C_EVENT)
    else:
        # OS likely supports signal interrupt
        signal.raise_signal(signal.SIGINT)


def clear() -> None:
    """Clears the screen of any output"""
    print('\n' * 100)
    if 'win' in get_platform().lower():
        os.system('cls')
    else:
        os.system('clear')


class App:
    def __init__(self, hub: Hub):
        # store hub object passed in, so the user can interact with delivery data
        self.hub = hub

        # pick up at the point where main() handed over execution
        # the user should be informed that all the data has been crunched
        input(f'Delivery data has been computed.\n\nPress <{Style.RED2}ENTER{Style.END}> to continue ...'
              f'{Style.GREEN1}\n> {Style.END}')

        # clear the screen before entering the infinite loop for the CLI
        clear()

    def run(self):
        # Set the kill signal event handler
        signal.signal(signal.SIGINT, _signal_handler)

        def display_search_results(results: list[Package] | list[list[Package]]) -> None:
            """Helper for handling if a search result is a list of packages, or multiple lists (one for each truck)"""
            if results:
                # Results were found
                if type(results[0]) is list:
                    # Results are multiple lists of packages ordered by truck
                    result_by_truck = f'{Style.UNDERLINE}Estimated delivery times{Style.END}\n' \
                                      f'The following packages were found:\n'
                    result_by_truck += f'{Style.YELLOW2}(Note: Packages are in sorted delivery order.){Style.END}\n\n'
                    results: list[list[Package]]

                    from copy import copy
                    from .util.time import to_digital_clock
                    for i, truck in enumerate(copy(results)):
                        eta = []
                        truck = sorted(truck, key=operator.attrgetter('delivered'))
                        result_by_truck += f'Packages on {Style.YELLOW2}Truck #00{i + 1}{Style.END}:\n\n'
                        for package in truck:
                            eta.append(package.delivered)
                            result_by_truck += package.printable() + '\n'
                        if not eta:
                            continue
                        eta = sorted(eta).pop()
                        eta = to_digital_clock(eta)
                        result_by_truck += f'Last delivery ETA: {eta}\n\n'
                    result_by_truck += f'Press <{Style.RED2}ENTER{Style.END}> to continue ...' \
                                       f'\n{Style.GREEN1}> {Style.END}'
                    input(result_by_truck)
                    clear()
                    return
                else:
                    # Result is one list of packages
                    _text = f'{Style.UNDERLINE}Estimated delivery times{Style.END}\n' \
                            f'The following packages were found:\n'
                    for package in packages:
                        _text += package.printable() + '\n'
                    _text += f'Press <{Style.RED2}ENTER{Style.END}> to continue ...{Style.GREEN1}\n> {Style.END}'
                    input(_text)
                    clear()
                    return
            else:
                # Results were not found
                _text = f'{Style.YELLOW2}No results to display.\n{Style.END}'
                _text += f'Press <{Style.RED2}ENTER{Style.END}> to continue ...{Style.GREEN1}\n> {Style.END}'
                input(_text)
                clear()

        def is_valid_numeric(string: str) -> bool:
            """Helper to check if text input is numeric"""
            if re.match(r'^[0123456789]+', string):
                return True
            return False

        # Begin Infinite Loop (CLI)
        while True:
            # A helpful list of options displayed to the user every iteration
            options = f'Type {Style.RED2}{Style.BOLD}\'help\'{Style.END} for command usage: \n\n' \
                      f'Available Commands:{Style.END}\n' \
                      f'{Style.RED2}{Style.BOLD}help:   ' \
                      f'{Style.END}{Style.ITALIC}\'displays help with commands\'\n{Style.END}' \
                      f'{Style.RED2}{Style.BOLD}lookup: ' \
                      f'{Style.END}{Style.ITALIC}\'looks up delivery information\'\n{Style.END}' \
                      f'{Style.RED2}{Style.BOLD}stats:  ' \
                      f'{Style.END}{Style.ITALIC}\'displays truck statistics\'\n{Style.END}' \
                      f'{Style.RED2}{Style.BOLD}quit:   ' \
                      f'{Style.END}{Style.ITALIC}\'exit the program\'\n{Style.END}' \
                      f'{Style.GREEN1}> {Style.END}'

            # Accept the user input
            cmd = input(options)

            # Handle input, match the user input to one of the following possibilities
            match cmd:

                # User wish to see help info
                case 'help':
                    text = f'\nCommand Usage:\n\n' \
                           f'{Style.RED2}{Style.UNDERLINE}{Style.BOLD}Lookup:{Style.END}\n\n' \
                           f'lookup [option] [arg]\n\n' \
                           f'Description:\n' \
                           f'Performs package lookups to retrieve delivery ETA on a package-by-package basis.\n' \
                           f'---------------------\n' \
                           f'Option | Arg | Desc.\n' \
                           f'---------------------\n' \
                           f'package  -a,   lookup package by ADDRESS\n' \
                           f'package  -d,   lookup package by DEADLINE\n' \
                           f'package  -c,   lookup package by CITY\n' \
                           f'package  -i,   lookup package by ID\n' \
                           f'package  -s,   lookup package by STATUS\n' \
                           f'package  -w,   lookup package by WEIGHT\n' \
                           f'package  -z,   lookup package by ZIP\n\n' \
                           f'{Style.RED2}{Style.UNDERLINE}{Style.BOLD}Stats:{Style.END}\n\n' \
                           f'stats [option]\n\n' \
                           f'Description:\n' \
                           f'The value parameter must be a TRUCK ID\n' \
                           f'---------------------\n' \
                           f'Option | Desc.\n' \
                           f'---------------------\n' \
                           f'truck,   lookup stats by TRUCK ID\n' \
                           f'route,   lookup planned routes by TRUCK ID\n\n' \
                           f'Press <{Style.RED2}ENTER{Style.END}> to continue ...' \
                           f'{Style.GREEN1}\n> {Style.END}'
                    input(text)
                    clear()

                # User is looking up all packages at a given time
                case 'lookup':
                    from .util import is_time_valid
                    search_key = input(f'Please enter a time in 24-hr format {Style.RED2}\'HH:MM\'{Style.END}:\n'
                                       f'{Style.GREEN1}> {Style.END}')
                    if is_time_valid(search_key) is True:
                        print(self.hub.snapshot(search_key))
                        input(f'Press <{Style.RED2}ENTER{Style.END}> to continue ...'
                              f'{Style.GREEN1}\n> {Style.END}')
                        clear()
                    else:
                        text = f'{Style.RED2}Format Invalid.{Style.END}\n>' \
                               f'Press <{Style.RED2}ENTER{Style.END}> to continue ...' \
                               f'{Style.GREEN1}\n> {Style.END}'
                        input(text)
                        clear()

                # User wants to search package(s), but did not specify the type of search
                case 'lookup package':
                    text = f'{Style.RED2}Missing required argument.{Style.END}\n' \
                           f'Please see help for command usage.\n' \
                           f'Press <{Style.RED2}ENTER{Style.END}> to continue ...' \
                           f'{Style.GREEN1}\n> {Style.END}'
                    input(text)
                    clear()

                # User wants to search package(s) by STREET address value
                case 'lookup package -a':
                    text = f'Please enter a STREET address or Press <{Style.RED2}ENTER{Style.END}> to display all ...' \
                           f'\n{Style.YELLOW2}(Note: partial address is OK){Style.END}\n' \
                           f'{Style.GREEN1}> {Style.END}'
                    search_key = input(text)
                    packages = self.hub.lookup_by_address(search_key)
                    display_search_results(packages)

                # User wants to search package(s) by CITY value
                case 'lookup package -c':
                    text = f'Please enter a CITY or Press <{Style.RED2}ENTER{Style.END}> to display all ...' \
                           f'\n{Style.YELLOW2}(Note: partial address is OK){Style.END}\n' \
                           f'{Style.GREEN1}> {Style.END}'
                    search_key = input(text)
                    packages = self.hub.lookup_by_city(search_key)
                    display_search_results(packages)

                # User wants to search package(s) with a given DEADLINE
                case 'lookup package -d':
                    text = f'Please enter a DEADLINE in the format {Style.RED2}\'HH:MM AM/PM\'\n' \
                           f'{Style.GREEN1}> {Style.END}'
                    search_key = input(text)
                    if search_key:
                        try:
                            search_key = datetime_from_string(search_key)
                            packages = self.hub.lookup_by_deadline(search_key)
                            display_search_results(packages)
                        except ValueError:
                            text = f'{Style.RED2}Format Invalid.{Style.END}\n>' \
                                   f'Press <{Style.RED2}ENTER{Style.END}> to continue ...' \
                                   f'{Style.GREEN1}\n> {Style.END}'
                            input(text)
                            clear()
                    else:
                        text = f'{Style.YELLOW2}Input is required to perform a search.\n{Style.END}' \
                               f'Press <{Style.RED2}ENTER{Style.END}> to continue ...' \
                               f'{Style.GREEN1}\n> {Style.END}'
                        input(text)
                        clear()

                # User wants to search a package with a given package ID
                case 'lookup package -i':
                    text = f'Please enter a package ID ...\n' \
                           f'{Style.GREEN1}> {Style.END}'
                    search_key = input(text)
                    if re.match(r'^[0123456789]+', search_key):
                        packages = [self.hub.lookup_by_id(int(search_key))]
                        display_search_results(packages)
                    else:
                        text = f'{Style.YELLOW2}No results to display.\n{Style.END}'
                        text += f'Press <{Style.RED2}ENTER{Style.END}> to continue ...{Style.GREEN1}\n> {Style.END}'
                        input(text)
                        clear()

                # User wants to search package(s) by status at a given time
                case 'lookup package -s':
                    text = f'Please enter a status:\n'
                    text += f'{Style.GREEN1}> {Style.END}'
                    status_key = input(text)
                    if status_key:
                        text = f'Please enter a time in the format {Style.RED2}\'HH:MM AM/PM\'{Style.END}:\n' \
                               f'{Style.GREEN1}> {Style.END}'
                        time_key = input(text)
                        packages = []
                        if time_key:
                            try:
                                time_key = datetime_from_string(time_key)
                                if 'd' in status_key:
                                    packages = self.hub.find_delivered_at_time(time_key)
                                elif 'e' in status_key:
                                    packages = self.hub.find_enroute_at_time(time_key)
                                elif 'h' in status_key:
                                    packages = self.hub.find_undelivered_at_time(time_key)
                                display_search_results(packages)
                            except ValueError:
                                text = f'{Style.RED2}Format Invalid.{Style.END}\n>' \
                                       f'Press <{Style.RED2}ENTER{Style.END}> to continue ...' \
                                       f'{Style.GREEN1}\n> {Style.END}'
                                input(text)
                                clear()
                        else:
                            display_search_results(packages)
                    else:
                        text = f'{Style.YELLOW2}Input is required to perform a search.\n{Style.END}' \
                               f'Press <{Style.RED2}ENTER{Style.END}> to continue ...{Style.GREEN1}\n> {Style.END}'
                        input(text)
                        clear()

                # User wants to search package(s) by weight
                case 'lookup package -w':
                    text = f'Please enter a WEIGHT:\n' \
                           f'{Style.GREEN1}> {Style.END}'
                    search_key = input(text)
                    if is_valid_numeric(search_key):
                        packages = self.hub.lookup_by_weight(search_key)
                        display_search_results(packages)
                    else:
                        text = f'{Style.RED2}Input must be numeric.\n{Style.END}'
                        text += f'Press <{Style.RED2}ENTER{Style.END}> to continue ...{Style.GREEN1}\n> {Style.END}'
                        input(text)
                        clear()

                # User wants to search package(s) by a 5-Digit ZIP code
                case 'lookup package -z':
                    text = f'Please enter a 5-digit ZIP:\n' \
                           f'{Style.GREEN1}> {Style.END}'
                    search_key = input(text)
                    if search_key:
                        if is_valid_numeric(search_key) and len(search_key) == 5:
                            packages = self.hub.lookup_by_zip(search_key)
                            display_search_results(packages)
                        else:
                            text = f'{Style.RED2}Input was not a 5-digit ZIP.\n{Style.END}'
                            text += f'Press <{Style.RED2}ENTER{Style.END}> to continue ...{Style.GREEN1}\n> {Style.END}'
                            input(text)
                            clear()
                    else:
                        text = f'{Style.RED2}Input is required to perform a search.\n{Style.END}'
                        text += f'Press <{Style.RED2}ENTER{Style.END}> to continue ...{Style.GREEN1}\n> {Style.END}'
                        input(text)
                        clear()

                # User wants to view distance statistics for all trucks
                case 'stats':
                    stats = self.hub.all_trip_distances() + '\n'
                    stats += f'(Note: To see route information for this truck, use the ' \
                             f'{Style.YELLOW2}`stats route`{Style.END} command)\n\n'
                    stats += f'Press <{Style.RED2}ENTER{Style.END}> to continue ...{Style.GREEN1}\n> {Style.END}'
                    input(stats)
                    clear()

                # User wants to view distance statistics for a specified truck ID
                case 'stats truck':
                    text = 'Please input truck ID:\n'
                    text += f'{Style.GREEN1}> {Style.END}'
                    search_key = input(text)
                    if is_valid_numeric(search_key) and 0 < int(search_key) <= self.hub.trucks + 1:
                        input(self.hub.trip_distance_by_truck(int(search_key) - 1))
                    else:
                        text = f'{Style.RED2}Input was not a valid truck ID.{Style.END}\n'
                        text += f'Press <{Style.RED2}ENTER{Style.END}> to continue ...{Style.GREEN1}\n> {Style.END}'
                        input(text)

                # User wants to view all planned routes for a given truck ID
                case 'stats route':
                    text = f'Please input truck ID:\n'
                    text += f'{Style.GREEN1}> {Style.END}'
                    search_key = input(text)
                    if is_valid_numeric(search_key) and 0 < int(search_key) < self.hub.trucks + 1:
                        input(self.hub.route_plan_by_truck_id(int(search_key) - 1))
                    else:
                        text = f'{Style.RED2}Input was not a valid truck ID.{Style.END}\n'
                        text += f'Press <{Style.RED2}ENTER{Style.END}> to continue ...{Style.GREEN1}\n> {Style.END}'
                        input(text)

                # User wants to exit the program
                case 'q':
                    kill()
                case 'quit':
                    kill()

                # Enter key was pressed with no input, or invalid command
                case _:
                    input(f'Command invalid.\nPress <{Style.RED2}ENTER{Style.END}> to continue ...'
                          f'{Style.GREEN1}\n> {Style.END}')
                    clear()

            # Clear the screen for the next loop iteration
            clear()
