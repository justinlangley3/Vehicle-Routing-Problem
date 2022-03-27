#
# Justin A. Langley
# Student ID: 001036634
# 2022-03-22
#

# STL
import signal
import sys

# Project
import cli
import adt
import util
from globals import Colors


def signal_handler(sig, frame):
    print("\nCtrl-C was pressed. Exiting ...")
    sys.exit(0)


def main():
    gps_path = './data/gps/'
    package_path = './data/package/'
    distance_path = './data/distance/'

    signal.signal(signal.SIGINT, signal_handler)

    header = f'\n' \
             f'{Colors.BLUE1}WGUPS Package Routing Progam{Colors.END}\n' \
             f'----------------------------\n' \
             f'Press {Colors.RED2}{Colors.LINE}Ctrl-C{Colors.END} at any time to exit.\n'
    usage = f'Usage: help [option]\n' \
            f'-l, --lookup\tpackage lookup\n' \
            f'-s, --sim\tdelivery simulation\n' \
            f'-m, --metrics\ttruck metrics\n' \
            f'-u, --update\tupdate package information\n'
    print(header)
    input(
        f'Please take a moment to import your data files.\n{Colors.YELLOW2}ENTER{Colors.END} to continue:\n{Colors.GREEN1}>{Colors.END} ')

    # Clear the screen and flush the buffer
    cli.cls()

    # Display some text and ask the user for a csv file
    print(f"{Colors.GREEN2}GPS Input{Colors.END}", flush=True)
    paths = cli.ls(gps_path, '.csv')
    gps_file = cli.file_choose(paths)
    addresses = util.parse_gps_data(gps_file)

    # Display some text and ask the user for a csv file
    print(f"{Colors.VIOLET1}Package Input{Colors.END}", flush=True)
    paths = cli.ls(package_path, '.csv')
    package_file = cli.file_choose(paths)
    packages = util.parse_package_data(package_file, addresses)

    # Display some text and ask the user for a csv file
    print(f"{Colors.YELLOW2}Distance Input{Colors.END}", flush=True)
    paths = cli.ls(distance_path, '.csv')
    distance_file = cli.file_choose(paths)
    print("\033[H\033[J", end="", flush=True)

    graph: structures.Graph = util.build_graph(addresses)

    # Program Loop
    while True:
        cmds = ["help", "delivery", "packages"]
        u_input = input(f"{Colors.RED2}-h{Colors.END}"
                        f" or "
                        f"{Colors.RED2}--help{Colors.END}"
                        f" for command usage help:\n"
                        f"{Colors.GREEN1}>{Colors.END} ")
        if u_input == "":
            pass
        elif u_input.lower() in ("-h", "--help"):
            cli.cmd_help(u_input)
            pass
        elif u_input.lower() in ("-s", "--simulate"):
            print("TODO")
            pass
        elif u_input.lower() in ("-l", "--lookup"):
            print("TODO")
            pass
        else:
            pass


if __name__ == '__main__':
    main()
