from __future__ import annotations

# STL
import operator
import time
from copy import copy, deepcopy
from datetime import datetime, timedelta

# Project Imports
from WGUPS.cli.style import Style
from WGUPS.structures.graph import Graph
from WGUPS.structures.hashtable import HashTable
from WGUPS.models.address import Address
from WGUPS.models.package import Package, PackageStatus
from WGUPS.models.truck import Truck


class Hub:
    _addresses: list[Address]
    _graph: Graph[Address]
    _packages: HashTable[int, Package]
    _trucks: list[Truck]

    # various package 'views'
    _delayed: set[Package]
    _dependencies: set[Package]
    _having_dependency: set[Package]
    _invalid: set[Package]
    _priority: set[Package]
    _standard: set[Package]

    # package 'views' by state
    _delivered: list[Package]

    # for separating packages with dependencies into resolved groups
    _dependency_chains: list[list[Package]]

    # containers for data related to delivery trips
    _trips: dict[datetime, list[int]]
    _trip_distances: list[list[float]]
    _departure_times: list[datetime]

    def __init__(self, addresses: list[Address], graph: Graph, packages: HashTable[int, Package], num_trucks: int = 2):

        self._addresses = addresses
        self._graph = graph
        self._packages = packages
        self.HUB = self._addresses[0]

        # 'views'
        self._delayed = set()
        self._dependencies = set()
        self._having_dependency = set()
        self._invalid = set()
        self._priority = set()
        self._standard = set()

        self._dependency_chains = list()
        self._remaining = [package for package in self._packages]

        # generate data for package 'views'
        # places packages into different categories
        self._generate_views()
        self._compute_dependency_chains()

        # initialize with empty trucks
        self._trucks = [Truck() for _ in range(num_trucks)]

        # setup containers for trip data
        self._trips = {}
        self._trip_distances = [list() for _ in range(len(self._trucks))]

        # initialize a list containing the last departure time for each truck initialized to 08:00 am
        today = datetime.today()

        # initialize all departure time 1 microsecond apart to keep keys unique
        self._departure_times = [datetime(today.year,
                                          today.month,
                                          today.day,
                                          8, 0, 0, x) for x in range(len(self._trucks))]

        self._dispatch_trucks()

    @property
    def trucks(self) -> int:
        """The number of trucks in the hub"""
        return len(self._trucks)

    def _prepare_shipments(self) -> None:
        """Mark all packages as ready for delivery"""
        for package in self._packages:
            package.set_status(PackageStatus.Hub)

    def reset_views(self) -> None:
        self._delayed.clear()
        self._dependencies.clear()
        self._having_dependency.clear()
        self._invalid.clear()
        self._priority.clear()
        self._standard.clear()

    def _compute_dependency_chains(self) -> None:
        """
        Builds package dependency chains i.e. groups of packages that must be delivered together.
        Once dependencies are resolved, the self._dependency_chain member is updated

        Example:
            Say we have the following subsets,
              where the first item in each set is the id of the package requiring the dependency:

              {1,2,3}, {5,3,4}, {20,21}, {23,20,21} {40,41}

            Outputs:
              A list containing:
                A list of packages with ids in the following subsets for each subset:

                {1,2,3,4,5}, {20,21,23}, {40,41}

        Returns: None

        """

        def _build_dependency_chains(f: list[set]) -> list[list[Package]]:
            """
            Turns all resolved dependencies sets into their package equivalents

            Args:
                f: list[set]

            Returns:

            """
            package_chain = []
            for subset in f:
                dep_ids = list(subset)
                to_add = [self._packages[int(pid)] for pid in dep_ids]
                for p in self._packages:
                    if p.id in dep_ids:
                        p.in_dependency_chain = True
                package_chain.append(to_add)
            return package_chain

        def _resolve(s: set, f: list[set]) -> None:
            """
            Given an expanded set,
            all sets in the forest fully included in the expanded set are removed from the forest

            Args:
                s: set
                f: list[set]

            Returns: None

            """
            to_remove = list()
            for subset in f:
                if subset & s == subset:
                    to_remove.append(subset)
            for item in to_remove:
                f.remove(item)

        def _expand(a: set, f: list[set]) -> set:
            """
            Unions the provided set with any other sets in the forest it has an intersection with
            This process is performed recursively

            Args:
                a: set
                f: list[set]

            Returns: set

            """
            if len(f) > 0:
                b = f.pop()
                if a.isdisjoint(b):
                    return _expand(a, f)
                else:
                    a = a | b
                    return _expand(a, f)
            return a

        if self._having_dependency is None:
            return

        forest = []
        for package in self._having_dependency:
            deps = package.has_dependency()
            new_set = set()
            new_set.add(package.id)
            for dep in deps:
                new_set.add(dep)
            forest.append(new_set)

        dependencies = list()
        while forest:
            current = _expand(forest.pop(), deepcopy(forest))
            _resolve(current, forest)
            dependencies.append(current)
        self._dependency_chains = _build_dependency_chains(dependencies)

    def _find_dependencies(self, p: Package) -> list[Package] | None:
        """
        Retrieves any dependent packages for a given package
        Then, removes these dependencies from
        Args:
            p: Package

        Returns: list[Package]

        """
        deps = p.has_dependency()
        if deps is not None:
            return [copy(self._packages[pid]) for pid in deps]

    def _get_dependency_chain(self, p: Package) -> list[Package] | None:
        """Get the dependency chain provided a package"""
        for chain in self._dependency_chains:
            if p in chain:
                return chain

    #
    # Package counts grouped by category
    #
    def _generate_views(self) -> None:
        """Counts packages by category and displays to the user"""

        def _add_special_handling(p: Package) -> None:
            """Add package to each category it was found in"""
            if p.has_delay():
                self._delayed.add(copy(p))
            if p.has_dependency() is not None:
                deps = self._find_dependencies(p)
                for dep in deps:
                    if dep not in self._dependencies:
                        self._dependencies.add(copy(dep))
                if p not in self._having_dependency:
                    self._having_dependency.add(copy(p))
            if p.has_invalid_flag():
                self._invalid.add(copy(p))
            if p.has_priority():
                self._priority.add(copy(p))
            if not (p.has_delay()
                    or p.has_dependency()
                    or p.has_invalid_flag()
                    or p.has_priority()):
                self._standard.add(copy(p))

        def _print_stats():
            """Print package category statistics to screen"""
            print(f'\n{Style.END}{Style.RED1}{len(self._invalid)}{Style.END} packages with an invalid address.')
            print(f'{Style.END}{Style.RED1}{len(self._having_dependency)}{Style.END} having dependencies.')
            print(f'{Style.END}{Style.YELLOW2}{len(self._dependencies)}{Style.END} which are dependencies.')
            print(f'{Style.END}{Style.YELLOW2}{len(self._delayed)}{Style.END} packages arriving late.')
            print(f'{Style.END}{Style.BLUE1}{len(self._priority)}{Style.END} with priority.')
            print(f'{Style.END}{Style.GREEN1}{len(self._standard)}{Style.END} with no special handling.\n')
            print('Done.')

        from WGUPS.cli.environment import progress, cls
        print(f'Computing special handling for: {len(self._packages)} packages')
        for package in progress(self._remaining):
            _add_special_handling(package)

        _print_stats()
        input(f'Press <{Style.RED1}Enter{Style.END}> to continue ...\n{Style.GREEN2}> {Style.END}')
        cls()

    def _update_master(self, package: Package) -> None:
        """Update a package in the master HashTable"""
        self._packages[int(package.id)] = package

    #
    # Truck Loading and Delivery Operations
    #
    def _load_remaining(self) -> None:
        """
        Performs sorting packages onto trucks for the given trip.
        A priority queue is used to load packages with the earliest deadline first.

        ~ O(N * M), Influenced by: ( total packages * number of trucks )
                    each truck is looped, but the while loop in each truck terminates when:
                    - The truck is full.
                    - No packages remain.

        Remaining checks when a package is pulled off the queue:
            - Has a truck requirement.
            - Was delayed, but it's arrival time has elapsed.
            - In a dependency chain. (If there is room on the truck, the package + all others in chain are loaded)
            - Address is invalid, but its update time has elapsed.

        On function call, if no packages remain, terminates immediately

        Load order:
            Priority packages

        Returns:

        """

        def receive_update(_to_update: Package):
            """Send an update to a package"""
            # The task requirements state that WGU doesn't know what the updates are until 10:30 am.
            # Since, we are precomputing deliveries, this information must be known in advance.
            # These two facts are in opposition with each other.

            # The only option is to allow the user to queue an update at runtime, then recompute all deliveries.
            # At the same time we don't know how many protected members of a package will be updated.
            # We also wouldn't know how many packages a user would place in the update batch.

            # The additional code to check for all of these intricacies,
            # seems greater than the scope of what this assessment is looking for.

            # processing a manual update
            if _to_update.id == 9:
                to_address = [address for address in self._addresses if address.street == '410 S State St']
                _to_update.address = to_address.pop()

        def is_loadable(_id: int, _to_load: package, _current: Truck) -> bool:
            """If even one check fails the package won't be loaded"""
            if _to_load.has_truck_requirement():
                if _to_load.has_truck_requirement() != _id + 1:
                    return False
            if _to_load.has_delay():
                if _to_load.has_delay() >= self._departure_times[_id].time():
                    return False
            if _to_load.in_dependency_chain:
                if self._dependency_chains:
                    if _current.capacity_remaining() < len(self._get_dependency_chain(_to_load)):
                        return False
                else:
                    return False
            if _to_load.has_invalid_flag():
                if update_time > self._departure_times[_id]:
                    return False
            return True

        def load(_next: Package, _current: Truck) -> None:
            """Load the next package onto the current truck, including any dependencies"""
            if _next.has_invalid_flag():
                receive_update(_to_update=_next)
                _current.load_package(_next)
                self._update_master(package=_next)
            if not _next.in_dependency_chain:
                _current.load_package(_next)
                self._update_master(package=_next)
            else:
                if self._dependency_chains is not None:
                    deps = self._get_dependency_chain(_next)
                    for dep in deps:
                        _current.load_package(dep)
                        self._update_master(package=dep)
                    self._dependency_chains.remove(deps)

        def find_earliest_deadline() -> Package:
            """Find the package with the earliest deadline"""
            _earliest: Package = self._remaining[0]
            for _p in self._packages:
                if _p.deadline < _earliest.deadline:
                    _earliest = _p
            return _earliest

        def update_remaining():
            """Forcibly update the list of remaining packages"""
            # Remaining = (Total - currently loaded - delivered)
            _loaded = list()
            for _t in self._trucks:
                for _p in _t:
                    _loaded.append(_p.id)
            for _p in self._packages:
                if _p.id not in _loaded:
                    if _p.status != PackageStatus.Delivered:
                        self._remaining.append(_p)

        if self._remaining is None:
            return

        today = datetime.today()  # time of day package updates are received
        update_time = datetime(today.year, today.month, today.day, 10, 20, 0, 0)

        queue = []  # dummy queue, so we can force it to clear, as needed
        for i, truck in enumerate(self._trucks):
            queue.clear()
            self._remaining.clear()
            update_remaining()

            if not self._remaining:
                return
            if len(self._remaining) == 1:
                earliest = self._remaining[-1]
            else:
                earliest = find_earliest_deadline()

            queue = [(earliest.deadline, earliest)]
            for package in self._remaining:
                if not (package.id == earliest.id):
                    queue.append((package.deadline, package))

            queue_contains = []
            queue_contains.extend(item[1].id for item in queue)
            queue = sorted(queue, reverse=True)
            while not truck.is_full():
                if queue:
                    to_load = queue.pop()[1]
                    if is_loadable(_id=i, _to_load=to_load, _current=truck):
                        from WGUPS.models.truck import AlreadyOnTruckError
                        try:
                            load(_next=to_load, _current=truck)
                        except AlreadyOnTruckError:
                            pass
                else:
                    break
        self._remaining.clear()
        update_remaining()

    def _dispatch_trucks(self):
        from WGUPS.cli.environment import progress
        print(f'Processing Delivery {Style.RED1}{Style.UNDERLINE}Routes:{Style.END}\n')
        count = 1
        while self._remaining:

            self._load_remaining()
            print(f'Computing delivery data for trip: {count} ...')
            for i, truck in enumerate(progress(self._trucks)):
                time.sleep((3 % count) * 0.5)
                if truck.packages is not None:
                    path = truck.optimize_delivery(_graph=self._graph, _hub=self.HUB)
                    if len(path) > 2:  # at least one package to deliver, the path includes the hub twice
                        self._deliver_packages_in_truck(truck_id=i, truck=truck, path=path)
                        for package in truck.packages:
                            self._update_master(package)
                        truck.clear()  # reset the truck for next iteration of load/delivery
                else:
                    # prevents deadlock, if packages remain, but require an update, haven't arrived, yet, etc.
                    # in that case, the current departure time needs to incremented until the issue resolves.
                    self._departure_times[i] += timedelta(seconds=1)
                    continue
            print()
            count += 1

    def _deliver_packages_in_truck(self, truck_id: int, truck: Truck, path: list[Address]) -> None:
        """
        Handles computing route distance and delivery time computations.
        Additionally, updates departure times, stores trips, and trip distances in their data structures.

        Complexity:
        O(n + m) - number of packages in the truck by number of edges in the path,
                   since this number is the same, runtime is on average O(n)

        Args:
            truck_id: int
            truck:  Truck
            path: list[Address]

        Returns: None

        """
        from WGUPS.util.time import calc_travel_time

        def _calc_distances(_path: list[Address]) -> tuple[float, list[tuple[Address, Address, float]]]:
            """
            Accepts a list of addresses, the 'path', that was optimized via the TSP module.
            Each 'leg' of the trip is calculated and stored as a list of tuples.
            The total distance is then calculated to be the distance sum of all the legs.
            Returns both total distance, and the list of legs as a tuple

            Args:
                _path: list[Address]

            Returns: tuple[int, list[tuple[Address, Address, float]]]

        """
            _seen = []
            _total: float = 0
            _prev_point = _path[0]
            _path.remove(_prev_point)
            while _path:
                _current = _path[0]
                _edge = (_prev_point, _current, self._graph[_prev_point][_current])
                _seen.append(_edge)
                _prev_point = _current
                _path.remove(_current)
            for _distance in _seen:
                _total += _distance[2] if _distance[2] is not None else 0.0
            return _total, _seen

        # store a copy of package ids in the trip, in a dict searchable by a datetime key
        clock = self._departure_times[truck_id]
        pids = copy(truck.pids)
        self._trips[clock] = pids

        # call subroutine to calculate distances
        total_distance, edges = _calc_distances(_path=path)
        for i, edge in enumerate(edges):
            if i == len(edges):
                break
            t = calc_travel_time(edge[2], truck.speed)
            clock += t  # update clock with current package

            for package in truck:
                if package.address == edge[1]:
                    package.delivered = clock
                    package.set_status(PackageStatus.Delivered)
                    self._update_master(package)

        if pids:
            # time taken to return to the hub must be added to the clock
            # this will be the next departure time, unless the truck must wait
            t = calc_travel_time(edges[-1][2], truck.speed)
            clock += t

            self._departure_times[truck_id] = clock
            self._trip_distances[truck_id].append(total_distance)
    #
    # End Truck Loading and Delivery Operations
    #

    #
    #   Functions for computing statistics
    #
    def mileage_total(self) -> float:
        """Total mileage of all trips for all trucks"""
        total = 0.0
        for trips in self._trip_distances:
            for trip in trips:
                total += trip
        return round(total, 1)

    def all_trip_distances(self) -> str:
        """Combined view of trip distances for each truck, and a combined total"""
        stats = f'{Style.YELLOW2}Distance Statistics:{Style.END}\n'
        for i in range(len(self._trucks)):
            stats += self.trip_distance_by_truck(i)
        stats += f'{Style.YELLOW2}Combined: {Style.UNDERLINE}{self.mileage_total()} mi{Style.END}\n'
        return stats

    def trip_distance_by_truck(self, truck_id: int) -> str:
        """Compute distance of all trips for a given truck."""
        stats = f'\n{Style.YELLOW2}Truck {Style.UNDERLINE}#00{truck_id + 1}:{Style.END}\n\n'
        trips = self._trip_distances[truck_id::len(self._trucks)]
        total = 0.0
        for i, trip in enumerate(trips):
            total += sum(trip)
        stats += f'Total Distance: {round(total, 1)} mi\n\n'
        return stats

    def trip_distance(self, truck_id: int, trip_id: int) -> float:
        """Compute the distance of a single trip by a given truck."""
        truck = self._trip_distances[truck_id::len(self._trucks)]
        for i, trip in enumerate(truck):
            return round(trip[trip_id], 1)

    def route_plan_by_truck_id(self, key: int):
        """Retrieve the route plans for a given truck"""
        stats = f'Route plans for {Style.YELLOW2}Truck {Style.UNDERLINE}#00{key + 1}:{Style.END}\n' \
                f'{Style.YELLOW2}(Note: Packages are in sorted delivery order.){Style.END}\n\n'
        trips = []
        for trip in self._trips.values():
            trips.append(trip)
        searched = trips[key::len(self._trucks)]
        for i, trip in enumerate(searched):
            stats += f'Trip {i + 1}:\n'
            stats += f'Planned Mileage: {self.trip_distance(truck_id=key, trip_id=i)} mi\n'
            packages = [copy(self._packages[int(pid)]) for pid in trip]
            packages = sorted(packages, key=operator.attrgetter('delivered'))
            for package in packages:
                package.set_status(PackageStatus.Hub)
                stats += package.printable() + '\n'
        return stats

    #
    #   Search/Lookup operations
    #
    def find_delivered_at_time(self, _time) -> list[Package]:
        """Finds all delivered packages at the provided time"""
        _all_delivered = []
        for _i, _package in self._packages.items():
            if _package.delivered <= _time:
                _all_delivered.append(copy(_package))
        return sorted(_all_delivered, key=operator.attrgetter('delivered'), reverse=True)

    def find_enroute_at_time(self, _time) -> list[list[Package]]:
        """Finds all enroute packages loaded on a truck at the provided time, separated by truck"""
        # microseconds are used to differentiate 'unique' initial departure times
        _all_enroute = [list() for _ in range(len(self._trucks))]
        _trucks = self._retrieve_time_window(_time)
        for _i, _truck in enumerate(_trucks):
            for _id in _truck:
                if self._packages[int(_id)].delivered > _time:
                    copy_of = copy(self._packages[int(_id)])
                    copy_of.set_status(PackageStatus.Enroute)
                    _all_enroute[_i].append(copy_of)
        for _i in range(len(_all_enroute)):
            _all_enroute[_i] = sorted(_all_enroute[_i], key=operator.attrgetter('delivered'), reverse=True)
        return _all_enroute

    def find_undelivered_at_time(self, _time) -> [list[Package]]:
        """Finds all undelivered packages at the provided time"""
        all_delivered = []
        enroute_ids = []
        _trucks = self._retrieve_time_window(_time)
        for _truck in _trucks:
            for _id in _truck:
                if self._packages[_id].delivered > _time:
                    enroute_ids.append(_id)
        for _package in self._packages:
            if _package.delivered > _time:
                if _package.id not in enroute_ids:
                    copy_of = copy(_package)
                    copy_of.set_status(PackageStatus.Hub)
                    all_delivered.append(copy_of)
        return sorted(all_delivered, key=operator.attrgetter('delivered'), reverse=True)

    def _retrieve_time_window(self, _time: datetime) -> list[list[int]]:
        """Finds the time window containing a searched time and returns truck trips occurring at that time"""
        _time += timedelta(microseconds=len(self._trucks))
        _time_windows: list[list[int]] = [list() for _ in range(len(self._trucks))]
        _i = 0
        for _departure, _pids in self._trips.items():
            if _departure <= _time:
                # storing the most recent trip at the given time for each truck
                # the current iteration mod len(trucks) will always give the correct truck
                _time_windows[_i % len(self._trucks)] = _pids
            _i += 1
        return _time_windows

    def lookup_by_id(self, key: int) -> Package:
        """Search for a package by its ID"""
        return copy(self._packages[int(key)])

    def lookup_by_address(self, street: str) -> list[Package]:
        """Search package(s) by address"""
        found = []
        for package in self._packages:
            if street in package.address.street:
                found.append(copy(package))
        return sorted(found, key=operator.attrgetter('id'))

    def lookup_by_deadline(self, search: datetime) -> list[Package]:
        """Search for package(s) by deadline"""
        found = []
        for package in self._packages:
            if package.deadline == search:
                found.append(copy(package))
        return sorted(found, key=operator.attrgetter('deadline'))

    def lookup_by_city(self, city: str) -> list[Package]:
        """Search for package(s) by city"""
        found = []
        for package in self._packages:
            if package.address.city == city:
                found.append(copy(package))
        return sorted(found, key=operator.attrgetter('id'))

    def lookup_by_zip(self, postal: str) -> list[Package]:
        """Search for package(s) by zip"""
        found = []
        for package in self._packages:
            if package.address.postal == postal:
                found.append(copy(package))
        return sorted(found, key=operator.attrgetter('id'))

    def lookup_by_weight(self, mass: str) -> list[Package]:
        """Search for package(s) by weight"""
        found = []
        for package in self._packages:
            if package.mass == int(mass):
                found.append(copy(package))
        return sorted(found, key=operator.attrgetter('id'))

    #
    # Views of all package statuses at a given time key
    #
    def snapshot(self, at_time: str) -> str:
        """
        Creates a 'snapshot' for packages at the requested time.
        Since all trips/routes are precomputed a clock 'unwinding' takes place to build the printout.
        Times can be 24hr format or include am/pm

        Args:
            at_time: str

        Returns: str

        """

        # noinspection DuplicatedCode
        def _make_snapshot_printable(_time, _at_hub: list[Package], _delivered: list[Package],
                                     _enroute: list[list[Package]]) -> str:
            """Make a printout view of the packages and their status"""
            # TODO: Apparently, f-strings are precomputed during initialization
            #       This causes them to print data, even when the if-conditions fail
            #
            #       The only solution so far:
            #         - Store a default value without package data added and compare
            #           ^ which, doesn't work well with loops in mind

            separator = '-' * 110 + '\n'
            _snapshot = f'{Style.UNDERLINE}Delivery Snapshot @ {_time}\n\n'
            header = f'{separator}' + '  '
            _cols = ('ID', 'Street', 'City', 'ST', 'Zip', 'KG' '    Status')
            widths = (2, 34, 14, 5, 4, 6, 6)
            for i, _col in enumerate(_cols):
                header += _col + (' ' * widths[i])
            header += f'\n'

            _hub_view = ''
            _hub_view_default = ''
            if _at_hub:
                _hub_view += f'{Style.RED1}Remaining:{Style.END}\n'
                _hub_view += f'{Style.RED1}{header}{Style.END}'
                _hub_view += f'{Style.RED1}{separator}{Style.END}'

                # update f-string default
                _hub_view_default += _hub_view
                _hub_view_default += f'{Style.RED1}{separator}{Style.END}\n'
                # end update f-string default

                for _package in _at_hub:
                    _hub_view += _package.printable() + '\n'
                _hub_view += f'{Style.RED1}{separator}{Style.END}\n'

            _enroute_view = ''
            _enroute_view_default = ''
            if _enroute:
                for i, _truck in enumerate(_enroute):
                    _enroute_view += f'{Style.YELLOW2}Enroute on ' \
                                     f'{Style.UNDERLINE}Truck #00{i + 1}' \
                                     f'{Style.END}{Style.YELLOW2}:\n{Style.END}'

                    _enroute_view += f'{Style.YELLOW2}{header}{Style.END}'
                    _enroute_view += f'{Style.YELLOW2}{separator}{Style.END}'

                    # update f-string default
                    _enroute_view_default += _enroute_view
                    _enroute_view_default += f'{Style.YELLOW2}{separator}{Style.END}\n'
                    # end update f-string default

                    for _package in _truck:
                        _enroute_view += _package.printable() + '\n'
                    _enroute_view += f'{Style.YELLOW2}{separator}{Style.END}\n'

            _delivered_view = ''
            _delivered_view_default = ''
            if _delivered:
                _delivered_view += f'{Style.GREEN1}Delivered:{Style.END}\n'
                _delivered_view += f'{Style.GREEN1}{separator}{Style.END}'

                # update f-string default
                _delivered_view_default += _delivered_view
                _delivered_view_default += f'{Style.GREEN1}{separator}{Style.END}'
                # end update f-string default

                for _package in _delivered:
                    _delivered_view += _package.printable() + '\n'
                _delivered_view += f'{Style.GREEN1}{separator}{Style.END}'

            if _hub_view != _hub_view_default:
                _snapshot += _hub_view
            if _enroute_view != _enroute_view_default:
                _snapshot += _enroute_view
            if _delivered_view != _delivered_view_default:
                _snapshot += _delivered_view

            return _snapshot

        from WGUPS.util.time import datetime_from_string
        search_key = datetime_from_string(at_time)

        enroute = self.find_enroute_at_time(_time=search_key)
        delivered = self.find_delivered_at_time(_time=search_key)
        at_hub = self.find_undelivered_at_time(_time=search_key)
        snapshot = _make_snapshot_printable(_time=at_time, _at_hub=at_hub, _delivered=delivered, _enroute=enroute)
        return snapshot

