#
# Justin A. Langley
# 2022-03-22
#
# noinspection PyUnusedLocal
def _exit_sig_handler(sig, frame):
    """Signal handler to exit gracefully on interrupt"""
    from sys import exit
    print("\nExiting ...")
    exit(0)


def clear() -> None:
    from os import system
    from WGUPS.cli.environment import get_platform
    print('\n' * 100)
    if 'win' in get_platform().lower():
        system('cls')
    else:
        system('clear')


def main():
    # STL
    import signal

    # Project imports
    import WGUPS.cli.io as io
    import WGUPS.cli.prompts as prompts
    from WGUPS.app import App
    from WGUPS.core.hub import Hub
    from WGUPS.cli.environment import get_platform

    # Set the interrupt handler for the kill signal
    signal.signal(signal.SIGINT, _exit_sig_handler)

    # function to clear the screen
    # it will often be used where data is presented to mitigate the user from having to scroll
    clear()

    # Greet the user, with a prompt to inform that data needs to be loaded in
    prompts.display_welcome()

    # Request data files from the user
    data_locations = ['./data/gps/', './data/package/']

    # handle cross-platform differences in file paths
    if 'win' in get_platform().lower():
        dir = __file__[:-7]
        data_locations = [dir+'data\\gps\\', dir+'data\\package\\']

    # Walk the user through selecting a file from each location above.
    # By default, the files in each directory are sorted by most recently modified
    gps_data_path, package_data_path = io.request_data_files(data_locations, '.csv')

    # Preliminary data processing for location data, given the user's file selection
    # First, all locations are transformed into address objects:
    #   - The Coordinate object for an address is created
    #   - Address is created with Coordinate object, and remaining csv data
    # Next, the graph is built:
    #   - Every Address is first added to the graph as a Vertex
    #   - Edges are created between each Address (Vertex) and every other (excluding itself)
    #   - Distance for each Edge is computed using a Ruler object from core.ruler
    #       + Ruler calculates distance using Haversine distance formula by default, but Vincenty can be used, as well
    graph, addresses = io.build_graph(path=gps_data_path)

    # Preliminary data processing for packages, given the user's file selection
    # A HashTable is built containing Package objects
    # This method requires a list of addresses to match a package to its corresponding Address object
    packages = io.build_packages(path=package_data_path, addresses=addresses)

    clear()

    # Create a hub object from data we retrieved via user input
    # Creating this object precomputes the following:
    #   + All special handling of packages
    #   + Trip distances
    #   + Truck departure times
    #   + Truck load plans (trips)
    #   + Package delivery order per trip, i.e. route optimization (passed to Solver object in core.tsp)
    # The core.hub and core.tsp are where 99% of the core logic is contained
    hub = Hub(addresses=addresses, graph=graph, packages=packages)

    # Initialize,
    # The app object is the core CLI.
    # Further user interactions occur here.
    app = App(hub=hub)

    # Begin infinite loop (core CLI)
    app.run()


if __name__ == '__main__':
    main()
