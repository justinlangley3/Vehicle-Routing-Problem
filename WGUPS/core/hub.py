from __future__ import annotations

# STL
import math
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
    # primary data structures
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

    # for separating packages with dependencies into their resolved groupings
    _dependency_chains: list[list[Package]]

    # additional data structures for data related to delivery trips
    _trips: dict[datetime, tuple[int, list[int]]]
    _trip_distances: list[list[float]]
    _departure_times: list[datetime]

    def __init__(self, addresses: list[Address], graph: Graph, packages: HashTable[int, Package], num_trucks: int = 2):
        # BEGIN Initialize primary data structures
        # store passed in data
        self._addresses = addresses
        self._graph = graph
        self._packages = packages
        self._trucks = [Truck(i) for i in range(num_trucks)]
        # END Initialize primary data structures

        # BEGIN Initialization of Package Categories
        # initialize 'views' as empty sets
        self._delayed = set()
        self._dependencies = set()
        self._having_dependency = set()
        self._invalid = set()
        self._priority = set()
        self._standard = set()
        # END Initialization of Package Categories

        # Set a variable containing the hub address, so it can be retrieved easily
        self.HUB = self._addresses[0]

        # BEGIN Initialization of Remaining Packages
        self._remaining = [package for package in self._packages]
        # END Initialization of Remaining Packages

        # generate the category data, store in set objects
        self._generate_views()

        # BEGIN Dependency Computations
        # create an empty list
        self._dependency_chains = list()
        # Compute Dependency Chains,
        # this is mostly some discrete math on sets occurring here.
        self._compute_dependency_chains()
        # The method first pulls IDs of all packages with dependencies, as well as dependents,
        # then, isolates them into groups by how much 'crossover' they have.
        # (packages with similar dependencies go in same group)
        # At that point they are assembled into lists of package objects and stored
        # END Dependency Computations

        # BEGIN Initialization of Truck Related Data Structures
        # setup containers for trip data
        self._trips = {}
        # initialize an empty list for containing last departure time by truck
        trip_count = math.ceil(len(self._packages) / len(self._trucks) / 16) + 1

        # ensuring we have a container big enough for both trucks
        # and that the containers are the same size, so we don't
        # run into issues running out of indices when looping
        dummy = []
        for _ in range(trip_count):
            dummy.append(0.0)
        self._trip_distances = [copy(dummy) for _ in range(len(self._trucks))]

        today = datetime.today()
        # initialize all departure time 1 microsecond apart to keep keys unique
        # this is required for all trucks to appear at the beginning of the day, so the trips dictionary
        # otherwise, the trips dict will overwrite one trip with another truck's trip data
        # a better solution should be implemented, but it works for the purposes of the task
        self._departure_times = [datetime(today.year,
                                          today.month,
                                          today.day,
                                          8, 0, 0, x) for x in range(len(self._trucks))]
        # END Initialization of Truck Related Data Structures

        # Begin Load/Delivery Optimization (Core Algorithm)
        self._dispatch_trucks()
        # End Load/Delivery Optimization

        # The class object is now ready for user interaction.

    @property
    def trucks(self) -> int:  # make it easy, externally, to get the truck count
        """The number of trucks in the hub"""
        return len(self._trucks)

    #
    # BEGIN Helper Methods
    #
    def _prepare_shipments(self) -> None:  # Unused, marked for delete
        """Mark all packages as ready for delivery"""
        for package in self._packages:
            package.set_status(PackageStatus.Hub)

    def reset_views(self) -> None:  # Unused, marked for delete
        """Clear all category 'views' """
        self._delayed.clear()
        self._dependencies.clear()
        self._having_dependency.clear()
        self._invalid.clear()
        self._priority.clear()
        self._standard.clear()

    def _update_master(self, package: Package) -> None:
        """Update a package in the master HashTable"""
        self._packages[int(package.id)] = package

    #
    # End Helper Methods
    #

    # BEGIN Dependency Chain Methods
    def _compute_dependency_chains(self) -> None:
        """
        Builds package dependency chains i.e. groups of packages that must be delivered together.
        Once dependencies are resolved, the self._dependency_chain member is updated

        Big-O Analysis:
          O(N^2): Expansion/Resolution increases the search space to n * n
                  Every n item, must be compared to every n other item.
                  The worst case considers that every package is a dependency of every other.
          Average case is O(n•k):
            This considers that the number of dependencies is likely a lot smaller than the total search space, and
            the total package data set need only be iterated for the number of packages with dependencies or
            depended on by another.

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
    # END Dependency Chain Methods
    #

    #
    # BEGIN Package Categorization Methods
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

    #
    # END Package Categorization Methods
    #

    #
    # Begin Truck Loading and Delivery Methods
    #
    def _load_remaining(self) -> None:
        """
        Core algorithm, which performs sorting packages onto trucks for the current set of trips.
        A priority queue is used to load packages with the earliest deadline first.

        Big-O Analysis:
        Worst Case:
          O(m•n•logn):
                Factors:
                    n items (packages) are iterated for updating the remaining queue
                    n items (packages) are sorted in the remaining queue to perform a priority queue
                    m items (loaded packages) per truck are iterated for updating the remaining queue
                Each item in the complete package data set is iterated by the number of trucks to build our list of
                remaining package. Since, m has some appropriate real world limit, and is guaranteed to include only
                some subset of n it should be negligible, but we include it anyways.
                (i.e. something like 1 truck per 1 package is insane, or 1 truck with all the packages is also insane).
                Once the list of remaining packages is formed, it gets sorted (nlogn) to form a priority queue.

                Since, we iterate our list twice (once with sort operations) this gives us O(n * logn).
                We don't perform any additional iterations for any item in n, so it doesn't grow exponentially.
                So, instead of 2n, for iterating it twice, we drop the constant.

                This leaves us with O(m•n•logn).

        On function call, if no packages remain, terminates immediately
        Load order:
            Priority packages (including late arrivals, or any included dependencies)
              Note: All below check described in Standard additionally occur on all priority packages
            Standard:
              Any not in the Priority category, including:
              - Has truck requirement
              - Late arrivals
              - Dependency chains
              - Packages with an invalid address, but have an update available

        Returns: None

        """

        # sequence of constant time operations, ignored in the Big-O analysis
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

        # sequence of constant time operations, ignored in the Big-O analysis
        def is_loadable(_id: int, _to_load: Package, _current: Truck) -> bool:
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
            # Big-O(n + k):
            #   Only when a package is in a dependency chain, requires checking n dependency chains with k items
            #   in each. Each chain will be a subset of the complete package data set, unless there is one dependency
            #   chain containing all packages, where it becomes O(n).
            #   If there are no dependencies then this method runs in constant time.
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

        def update_remaining() -> None:
            """
            Forcibly update the list of remaining packages
            Big-O Analysis:
                O(m•n):
                        Data Set Operations (partial):
                        We consider getting the list of loaded package ids as O(m + k).
                        Each truck must be iterated and an empty list extended by a factor of k per truck,
                        so is influenced linearly by O(k), for k items added the number of packages loaded per truck,
                        which can vary in size, but artificially limited by truck capacity (16 in our case). So, k
                        drops out to be a sequence of constant time operations. When the number of trucks becomes
                        very large, we are performing this operation on each truck.

                        Consider in the real world, there will be a maximum number of trucks we have.
                        Also, m is guaranteed to be less the number of delivered packages due to the truck capacity.

                        It makes sense to characterize this operation separately as m is therefore a tunable parameter,
                        and guaranteed to be less than n in our use case i.e. we can't have more packages loaded
                        than total packages than we have.
                        Thus, the worst case of this operation is O(m), where m is the number of trucks iterated.

                        Data Set Operations (complete):
                        Additionally, we consider building the list of remaining packages to be O(n).
                        Each package in the complete data set must be compared to the smaller subset of package ids
                        per loaded truck, by calling the 'in' operator ...

                        Therefore, in the worst case we are performing 16 comparisons per package in complete
                        list of all packages multiplied by the number of trucks.

                        Combining the worst case of each we end up with O(m•n).

            Returns: None

            """
            # Remaining = (Total - currently loaded - delivered)
            _loaded: list[int] = []
            for _truck in self._trucks:
                _loaded.extend(_truck.pids)
            for _p in self._packages:
                if _p.id not in _loaded:
                    if _p.status != PackageStatus.Delivered:
                        self._remaining.append(deepcopy(_p))

        if self._remaining is None:
            return

        today = datetime.today()  # time of day package updates are received
        update_time = datetime(today.year, today.month, today.day, 10, 20, 0, 0)

        # Initialize a queue to be used as a Priority Queue
        queue = []  # dummy queue
        for i, truck in enumerate(self._trucks):
            # Clear of any previous iteration
            # ( guarding against loading the same items more than once )
            queue.clear()
            self._remaining.clear()
            update_remaining()

            # Discontinue if no packages remain to load
            if not self._remaining:
                return
            if len(self._remaining) == 1:
                queue = [self._remaining[-1]]
            else:
                # Transform remaining items into a priority queue
                # O(nlogh), the complexity of python's internal timsort
                queue = sorted(self._remaining, key=operator.attrgetter('deadline'), reverse=True)

            # while truck has capacity remaining
            while not truck.is_full():
                if queue:  # still has items,
                    # continue loading
                    to_load = queue.pop()

                    if is_loadable(_id=i, _to_load=to_load, _current=truck):
                        from WGUPS.models.truck import AlreadyOnTruckError
                        try:
                            # O(n * m)
                            load(_next=to_load, _current=truck)
                        except AlreadyOnTruckError:
                            # package is already on the truck,
                            # proper guarding is in place to simply consume the Error
                            pass
                else:
                    # stop loading
                    break

        # Finished loading trucks,
        # Clear the remaining package list
        self._remaining.clear()

        # Create a new list of remaining items,
        # one that won't include what was loaded
        update_remaining()

    def _dispatch_trucks(self) -> None:
        """
        Core algorithm for controlling both loading and delivery of packages onboard trucks.

        Big-O Analysis:
          O(m•n^2•logn):
            The combination of the runtime complexity of the load optimization algorithm,
            the path optimization algorithm, and the delivery algorithm.

            The load optimization is (m•n•logn), where m is # trucks and n is # packages
            The path optimization is (n^2•logh), where h is the subset of n that forms the boundary (hull)
            The delivery algorithm is O(n), where n is the number of edges in the path visited

            We need to simplify the complexities somewhat to find a more easily understandable upper bound.
            One thing is the path optimization can be considered O(n^2) since the insertion sort inside it
            completely dwarfs the complexity to find the hull.

            Combining it we get: O(m•n^2•logn), we can ignore the linear complexity of the delivery algorithm.

            With this, we know our algorithm is greater than n^2, but we don't think it's enough to call it
            n^3, since m, the number of truck operations performed is likely to be far smaller than n.

            That said, the combination of our algorithms has quite a bad runtime, but it beats out the time complexity
            to brute force the traveling salesperson problem, which would be O(n!).

            If we optimized our data structures further.
            One example, we could create layers to our convex hull algorithm, where we find successive convex hulls on
            the inner points within the boundary of the hull. Then, with a divide and conquer approach they could be
            merged to form the optimal path. With this kind of approach our solution should easily go to linearithmic
            time complexity.

        Returns: None

        """
        # inform the user of what we're currently processing
        from WGUPS.cli.environment import progress
        print(f'Processing Delivery {Style.RED1}{Style.UNDERLINE}Routes:{Style.END}\n')

        # use a list for storing # of trips per truck, as it may vary
        trip_counts = [0] * len(self._trucks)
        while self._remaining:  # while packages still remain to be delivered
            # Load packages onto trucks
            self._load_remaining()

            # For each truck, perform with progress indication
            print('Computing optimal trips: ', trip_counts)
            for i, truck in enumerate(progress(self._trucks)):
                time.sleep(sum(trip_counts) * 0.1)
                if truck.packages is not None:
                    # Truck has packages to deliver,
                    # Optimize the route plan ( O(nlogh) runtime for convex hull, output sensitive )
                    path = truck.optimize_delivery(_graph=self._graph, _hub=self.HUB)

                    # Check path length, note: the path includes the hub twice to explain the condition check
                    if len(path) > 2:
                        # at least one package is on the truck

                        # Perform package delivery
                        self._deliver_packages_in_truck(trip_id=trip_counts[i], truck=truck, path=path)

                        for package in truck.packages:
                            self._update_master(package)

                        # reset the truck for next iteration of load/delivery
                        truck.clear()
                    trip_counts[i] += 1
                else:
                    # No packages are on the truck,
                    # We must be careful to guard against deadlock here (infinite looping)

                    # If we are here, packages remain, but require an update, haven't arrived, yet, etc.
                    # in that case, the current departure time needs to incremented until the departure time
                    # has progressed far enough for those issues to resolve the checks in the loading routine
                    self._departure_times[i] += timedelta(seconds=1)
                    continue  # proceed with an updated departure time
            print()  # print empty line

    def _deliver_packages_in_truck(self, trip_id: int, truck: Truck, path: list[Address]) -> None:
        """
        Handles computing route distance and delivery time computations.
        Additionally, updates departure times, stores trips, and trip distances in their data structures.

        Complexity:
            O(n):
               number of edges in the path, by the number of packages in the truck

               For our purpose, since the truck capacity is fixed and small, we will consider package searches per
               edge iteration to be a constant time operation.

               The number of packages in the truck also reduces by 1 each edge iteration, reducing further iterations
               ( the linear sequence k(k-1), where k is truck capacity ).

               Therefore, the runtime is linear by the number of edges in the path O(n).

               If the Truck included a HashTable of address, package key/value pairs, this could be further guaranteed
               to be O(n) as then the ending Address of the iterated edge would be the key to access the package
               onboard the truck. In this case only the edges would have to be iterated once.
               We will treat this as if we had an optimal solution to simplify the Big-O analysis of our
               truck dispatching algorithm

        Args:
            trip_id: int
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
            self._trip_distances[truck.truck_id][trip_id] += _total
            return _total, _seen

        # store a copy of package ids in the trip, in a dict searchable by a datetime key
        clock = self._departure_times[truck.truck_id]
        pids = copy(truck.pids)
        self._trips[clock] = (truck.truck_id, pids)

        # call subroutine to calculate distances
        total_distance, edges = _calc_distances(_path=path)
        for i, edge in enumerate(edges):
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
            self._departure_times[int(truck.truck_id)] = clock

    #
    # END Truck Loading and Delivery Methods
    #

    #
    # BEGIN Statistics Methods
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
        stats = f'\n{Style.YELLOW2}Truck {Style.UNDERLINE}#00{truck_id + 1}:{Style.END}\n'
        total = round(sum(self._trip_distances[truck_id]), 1)
        stats += f'Total Distance: {total} mi\n\n'
        return stats

    def trip_distance(self, truck_id: int, trip_id: int) -> float:
        """Compute the distance of a single trip by a given truck."""
        truck = self._trip_distances[truck_id]
        return round(truck[trip_id], 1)

    def route_plan_by_truck_id(self, key: int):
        """Retrieve the route plans for a given truck"""
        stats = f'Route plans for {Style.YELLOW2}Truck {Style.UNDERLINE}#00{key + 1}:{Style.END}\n' \
                f'{Style.YELLOW2}(Note: Packages are in sorted delivery order.){Style.END}\n\n'
        trips = []
        for trip in self._trips.values():
            trips.append(trip)

        i = 0
        for trip in self._trips.values():
            if trip[0] != key:
                continue

            # f-string would update the variable if we add 1
            # that would cause route data lookups to display incorrect results
            j = i + 1

            stats += f'Trip {j}:\n'
            stats += f'Planned Mileage: {self.trip_distance(truck_id=key, trip_id=i)} mi\n'
            packages = [copy(self._packages[int(pid)]) for pid in trip[1]]
            packages = sorted(packages, key=operator.attrgetter('delivered'))
            for package in packages:
                package.set_status(PackageStatus.Hub)
                stats += package.printable() + '\n'
            i += 1

        return stats

    #
    # END Statistics Methods
    #

    #
    # BEGIN Search/Lookup Methods
    #
    def find_delivered_at_time(self, _time) -> list[Package]:
        """Finds all delivered packages at the provided time"""
        _all_delivered = []
        for _i, _package in self._packages.items():
            if _package.delivered and _package.delivered <= _time:
                _all_delivered.append(copy(_package))
        return sorted(_all_delivered, key=operator.attrgetter('delivered'), reverse=True)

    def find_enroute_at_time(self, _time) -> list[list[Package]]:
        """Finds all enroute packages loaded on a truck at the provided time, separated by truck"""
        # microseconds are used to differentiate 'unique' initial departure times
        _all_enroute = [list() for _ in range(len(self._trucks))]
        _trucks = self._retrieve_trip_window(_time)
        if not _trucks:
            return [[]]
        for _i, _ids in enumerate(_trucks):
            if not _ids:
                return [[]]
            _truck_id, _pids = _ids[0], _ids[1]
            for _pid in _pids:
                if _truck_id == _i and self._packages[int(_pid)].delivered > _time:
                    copy_of = copy(self._packages[int(_pid)])
                    copy_of.set_status(PackageStatus.Enroute)
                    _all_enroute[_i].append(copy_of)
        for _i in range(len(_all_enroute)):
            # Sort packages so they are shown in delivery sequence
            _all_enroute[_i] = sorted(_all_enroute[_i], key=operator.attrgetter('delivered'))
        return _all_enroute

    def find_undelivered_at_time(self, _time) -> list[Package]:
        """Finds all undelivered packages at the provided time"""
        all_delivered = []
        enroute_ids = []
        _trucks = self._retrieve_trip_window(_time)
        if not _trucks:
            return []
        for _i, _ids in enumerate(_trucks):
            if not _ids:
                return []
            _truck_id, _pids = _ids[0], _ids[1]
            for _pid in _pids:
                if self._packages[_pid].delivered > _time:
                    enroute_ids.append(_pid)
        for _package in self._packages:
            if _package.delivered and _package.delivered > _time:
                if _package.id not in enroute_ids:
                    copy_of = copy(_package)
                    copy_of.set_status(PackageStatus.Hub)
                    all_delivered.append(copy_of)
        return sorted(all_delivered, key=operator.attrgetter('delivered'), reverse=True)

    def _retrieve_trip_window(self, _time: datetime) -> list[tuple[int, list[int]]]:
        """Finds the trip data in the time window of a searched time and returns truck trips occurring at that time"""
        _time += timedelta(microseconds=len(self._trucks))
        _time_windows: list[tuple[int, list[int]]] = [tuple() for _ in range(len(self._trucks))]
        _i = 0
        for _departure, _pids in self._trips.items():
            if _departure <= _time:
                # storing the most recent trip at the given time for each truck
                # the current iteration mod len(trucks) will always give the correct truck
                _time_windows[_pids[0]] = _pids
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
    # END Search/Lookup Methods
    #

    #
    # BEGIN Special Print Methods
    #
    def snapshot(self, at_time: str) -> str:
        """
        Creates a 'snapshot' for packages at the requested time.
        Since all trips/routes are precomputed a clock 'unwinding' takes place to build the printout.
        Times can be 24hr format or include am/pm.

        Big-O Analysis:
            Approx. O(nk), we iterate our package data structure 3 times to get delivery information.


        Args:
            at_time: str

        Returns: str

        """

        # noinspection DuplicatedCode
        def _make_snapshot_printable(_search_key, _time, _at_hub: list[Package], _delivered: list[Package],
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
                    # display package that was updated properly
                    # a 'history' of changes would be stored in the object, but,
                    # for now we're reverting it manually
                    today = datetime.today()
                    update = datetime(today.year, today.month, today.day, 10, 20)
                    if _package.id == 9:
                        if _search_key < update:
                            _package.address = self._addresses[12]
                        else:
                            _package.address = self._addresses[19]

                    _hub_view += _package.printable() + '\n'
                _hub_view += f'{Style.RED1}{separator}{Style.END}\n'
            else:
                _hub_view += f'{Style.END}{Style.RED2}{Style.BOLD}No packages in hub at this time.{Style.END}\n\n'

            _enroute_view = ''
            _enroute_view_default = ''
            if _enroute:
                for i, _truck in enumerate(enroute):
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

        # transform user search input into a datetime object
        from WGUPS.util.time import datetime_from_valid_input
        search_key = datetime_from_valid_input(at_time)

        # build the 'views' by category
        at_hub = self.find_undelivered_at_time(_time=search_key)
        enroute = self.find_enroute_at_time(_time=search_key)
        delivered = self.find_delivered_at_time(_time=search_key)

        # make a printout with the categorized package data
        snapshot = _make_snapshot_printable(_at_hub=at_hub,
                                            _delivered=delivered,
                                            _enroute=enroute,
                                            _time=at_time,
                                            _search_key=search_key)
        return snapshot
    #
    # END Special Print Methods
    #
