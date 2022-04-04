# STL
import operator
import os
import re
import signal
import sys

# Project imports
from .core.hub import Hub
from .cli.environment import cls
from .cli.style import Style
from .models import Package
from .util.time import datetime_from_string


# noinspection PyUnusedLocal
def _signal_handler(sig, frame):
    print("\nCtrl-C was pressed. Exiting ...")
    sys.exit(0)


class App:
    def __init__(self, hub: Hub):
        self.hub = hub
        # inform the user that the hub object is done computing before they are dropping into the CLI
        input(f'Delivery data has been computed.\nPress <{Style.RED2}ENTER{Style.END}> to continue ...'
              f'{Style.GREEN1}\n> {Style.END}')
        cls()

    def run(self):
        signal.signal(signal.SIGINT, _signal_handler)

        def clear() -> None:
            from WGUPS.cli.environment import get_platform
            print('\n'*100)
            if 'win' in get_platform():
                os.system('cls')
            else:
                os.system('clear')

        def display_search_results(results: list[Package] | list[list[Package]]) -> None:
            if results:
                if type(results[0]) is list:
                    result_by_truck = f'{Style.UNDERLINE}Estimated delivery times{Style.END}\n' \
                                      f'The following packages were found:\n'
                    result_by_truck += f'{Style.YELLOW2}(Note: Packages are in sorted delivery order.){Style.END}\n\n'
                    results: list[list[Package]]

                    from copy import copy
                    from .util.time import to_digital_clock
                    for i, truck in enumerate(copy(results)):
                        eta = []
                        truck = sorted(truck, key=operator.attrgetter('delivered'))
                        result_by_truck += f'Packages on {Style.YELLOW2}Truck #00{i+1}{Style.END}:\n\n'
                        for package in truck:
                            eta.append(package.delivered)
                            result_by_truck += package.printable() + '\n'
                        if not eta:
                            continue
                        eta = sorted(eta).pop()
                        eta = to_digital_clock(eta)
                        result_by_truck += f'Last delivery ETA: {eta}\n\n'
                    result_by_truck += f'Press <{Style.RED2}ENTER{Style.END}> to continue ...' \
                                       f'{Style.GREEN1}\n> {Style.END}'
                    input(result_by_truck)
                    clear()
                    return
                else:
                    _text = f'{Style.UNDERLINE}Estimated delivery times{Style.END}\n' \
                            f'The following packages were found:\n'
                    for package in packages:
                        _text += package.printable() + '\n'
                    _text += f'Press <{Style.RED2}ENTER{Style.END}> to continue ...{Style.GREEN1}\n> {Style.END}'
                    input(_text)
                    clear()
                    return
            else:
                _text = f'{Style.YELLOW2}No results to display.\n{Style.END}'
                _text += f'Press <{Style.RED2}ENTER{Style.END}> to continue ...{Style.GREEN1}\n> {Style.END}'
                input(_text)
                clear()

        def is_valid_numeric(string: str) -> bool:
            if re.match(r'^[0123456789]+', string):
                return True
            return False

        while True:
            options = f'Type {Style.RED2}{Style.BOLD}\'help\'{Style.END} for command usage: \n\n' \
                      f'Available Commands:{Style.END}\n' \
                      f'{Style.RED2}{Style.BOLD}help:   ' \
                      f'{Style.END}{Style.ITALIC}\'displays help with commands\'\n{Style.END}' \
                      f'{Style.RED2}{Style.BOLD}lookup: ' \
                      f'{Style.END}{Style.ITALIC}\'looks up delivery information\'\n{Style.END}' \
                      f'{Style.RED2}{Style.BOLD}stats:  ' \
                      f'{Style.END}{Style.ITALIC}\'displays truck statistics\'\n{Style.END}' \
                      f'{Style.GREEN1}> {Style.END}'
            cmd = input(options)

            match cmd:
                case 'help':
                    text = f'\nCommand Usage:\n\n' \
                           f'{Style.RED2}{Style.UNDERLINE}{Style.BOLD}Lookup:{Style.END}\n\n' \
                           f'-lookup [option] [arg]\n\n' \
                           f'Description:\n' \
                           f'Performs package lookups to retrieve delivery ETA on a package-by-package basis.\n' \
                           f'---------------------\n' \
                           f'Option | Arg | Desc.\n' \
                           f'---------------------\n' \
                           f'-package  -a,   lookup package by ADDRESS\n' \
                           f'-package  -d,   lookup package by DEADLINE\n' \
                           f'-package  -c,   lookup package by CITY\n' \
                           f'-package  -i,   lookup package by ID\n' \
                           f'-package  -s,   lookup package by STATUS\n' \
                           f'-package  -w,   lookup package by WEIGHT\n' \
                           f'-package  -z,   lookup package by ZIP\n\n' \
                           f'{Style.RED2}{Style.UNDERLINE}{Style.BOLD}Stats:{Style.END}\n\n' \
                           f'-stats [option]\n\n' \
                           f'Description:\n' \
                           f'The value parameter must be a TRUCK ID\n' \
                           f'---------------------\n' \
                           f'Option | Desc.\n' \
                           f'---------------------\n' \
                           f'-truck,   lookup stats by TRUCK ID\n' \
                           f'-route,   lookup planned routes by TRUCK ID\n\n' \
                           f'Press <{Style.RED2}ENTER{Style.END}> to continue ...' \
                           f'{Style.GREEN1}\n> {Style.END}'
                    input(text)
                    clear()
                case 'lookup':
                    text = input(f'Please enter a time in the format {Style.RED2}\'HH:MM AM/PM\'{Style.END}:\n'
                                 f'{Style.GREEN1}> {Style.END}')
                    try:
                        from WGUPS.util import time_from_string
                        time_from_string(text)
                        print(self.hub.snapshot(text))
                        input(f'Press <{Style.RED2}ENTER{Style.END}> to continue ...'
                              f'{Style.GREEN1}\n> {Style.END}')
                        clear()
                    except IndexError:
                        text = f'{Style.RED2}Format Invalid.{Style.END}\n>' \
                               f'Press <{Style.RED2}ENTER{Style.END}> to continue ...' \
                               f'{Style.GREEN1}\n> {Style.END}'
                        input(text)
                        clear()
                case 'lookup -package':
                    text = f'{Style.RED2}Missing required argument.{Style.END}\n' \
                           f'Please see help for command usage.\n' \
                           f'Press <{Style.RED2}ENTER{Style.END}> to continue ...' \
                           f'{Style.GREEN1}\n> {Style.END}'
                    input(text)
                    clear()
                case 'lookup -package -a':
                    text = f'Please enter a STREET address or Press <{Style.RED2}ENTER{Style.END}> to display all ...' \
                           f'\n{Style.YELLOW2}(Note: partial address is OK){Style.END}\n' \
                           f'{Style.GREEN1}> {Style.END}'
                    search_key = input(text)
                    packages = self.hub.lookup_by_address(search_key)
                    display_search_results(packages)
                case 'lookup -package -c':
                    text = f'Please enter a CITY or Press <{Style.RED2}ENTER{Style.END}> to display all ...' \
                           f'\n{Style.YELLOW2}(Note: partial address is OK){Style.END}\n' \
                           f'{Style.GREEN1}> {Style.END}'
                    search_key = input(text)
                    packages = self.hub.lookup_by_city(search_key)
                    display_search_results(packages)
                case 'lookup -package -d':
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
                case 'lookup -package -i':
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
                case 'lookup -package -s':
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
                case 'lookup -package -w':
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
                case 'lookup -package -z':
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
                case 'stats':
                    stats = self.hub.all_trip_distances() + '\n'
                    stats += f'(Note: To see route information for this truck, use the ' \
                             f'{Style.YELLOW2}`stats -route`{Style.END} command)\n\n'
                    stats += f'Press <{Style.RED2}ENTER{Style.END}> to continue ...{Style.GREEN1}\n> {Style.END}'
                    input(stats)
                    clear()
                case 'stats -truck':
                    text = 'Please input truck ID:\n'
                    text += f'{Style.GREEN1}> {Style.END}'
                    search_key = input(text)
                    if is_valid_numeric(search_key) and 0 < int(search_key) <= self.hub.trucks + 1:
                        input(self.hub.trip_distance_by_truck(int(search_key) - 1))
                    else:
                        text = f'{Style.RED2}Input was not a valid truck ID.{Style.END}\n'
                        text += f'Press <{Style.RED2}ENTER{Style.END}> to continue ...{Style.GREEN1}\n> {Style.END}'
                        input(text)
                case 'stats -route':
                    text = f'Please input truck ID:\n'
                    text += f'{Style.GREEN1}> {Style.END}'
                    search_key = input(text)
                    if is_valid_numeric(search_key) and 0 < int(search_key) <= self.hub.trucks + 1:
                        input(self.hub.route_plan_by_truck_id(int(search_key) - 1))
                    else:
                        text = f'{Style.RED2}Input was not a valid truck ID.{Style.END}\n'
                        text += f'Press <{Style.RED2}ENTER{Style.END}> to continue ...{Style.GREEN1}\n> {Style.END}'
                        input(text)
                case _:
                    input(f'Command invalid.\nPress <{Style.RED2}ENTER{Style.END}> to continue ...'
                          f'{Style.GREEN1}\n> {Style.END}')
                    clear()
            cls()
