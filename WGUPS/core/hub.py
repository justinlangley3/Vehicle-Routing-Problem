from __future__ import annotations

import pprint
from copy import copy, deepcopy

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
    _delayed: list[Package]
    _dependencies: list[Package]
    _dependency_chains: list[list[Package]]
    _having_dependency: list[Package]
    _invalid: list[Package]
    _priority: list[Package]
    _standard: list[Package]

    # containers for packages in various states
    _delivered: set[Package]
    _enroute: set[Package]
    _remaining: set[Package]

    def __init__(self, addresses: list[Address], graph: Graph, packages: HashTable[int, Package], num_trucks: int = 3):

        self._addresses = addresses
        self._graph = graph
        self._packages = packages
        self.HUB = self._addresses[0]

        # initialize package 'views'
        # these lists categorize packages by type
        # packages contained here are shallow copies
        self._delayed = list()
        self._dependencies = list()
        self._dependency_chains = list()
        self._having_dependency = list()
        self._invalid = list()
        self._priority = list()
        self._standard = list()

        # initialize all packages with a status of 'In Hub'
        # self._prepare_shipments()
        # not needed, packages are initialized as in hub

        # generate data for package 'views'
        # places packages into different categories
        self._generate_views()
        self._compute_dependency_chains()

        # 'views' by status
        self._delivered = set()
        self._enroute = set()
        self._remaining = set()

        # setup trucks
        self._trucks = [Truck() for _ in range(num_trucks)]
        self._initialize_trucks()
        self._dispatch_trucks()

        self._update_remaining()

    def _prepare_shipments(self) -> None:
        """
        Update package statuses, so they appear at the hub location
        Returns: None

        """
        for package in self._packages:
            package.set_status(PackageStatus.Hub)

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
                to_add = [copy(self._packages[int(pid)]) for pid in dep_ids]
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
        for chain in self._dependency_chains:
            if p in chain:
                return chain

    def _initialize_trucks(self) -> None:
        """
        Initializes trucks with optimizations toward handling dependency chains and priority first
        Attempts to distribute packages between trucks evenly
        Returns: None

        """
        def _detect_priority_with_dependencies() -> list[Package]:
            for _package in self._priority:
                _chain = self._get_dependency_chain(_package)
                if _chain is not None:
                    return copy(_chain)

        def _isolate_priority_with_dependencies(_chain: list[Package]) -> None:
            for _package in _chain:
                if _package in self._priority:
                    self._priority.remove(_package)

        def _handle_priority_with_dependencies(_chain: list[Package], _truck: Truck) -> None:
            if _truck.has_capacity() and _truck.has_capacity() >= len(_chain):
                for _package in _chain:
                    _truck.load_package(_package)
                    self._checkout_package(_package)

        already_used = []
        # handle dependency chains with priority packages in them upfront
        # only one dependency chain per truck will be handled
        while len(self._dependency_chains) > 0:
            for i in range(len(self._trucks)):
                detected = _detect_priority_with_dependencies()
                if detected and self._trucks[i].has_capacity() >= len(detected):
                    _isolate_priority_with_dependencies(_chain=detected)
                    _handle_priority_with_dependencies(_chain=detected, _truck=self._trucks[i])
                    self._dependency_chains.remove(detected)
                    already_used.append(i)
            break

        for i, truck in enumerate(self._trucks):
            if i not in already_used and self._priority is not None:
                for package in copy(self._priority):
                    dep = package.has_dependency()
                    delay = package.has_delay()
                    truck_req = package.has_truck_requirement()
                    invalid = package.has_invalid_flag()
                    if (truck_req and truck_req != i) or dep or delay or invalid:
                        continue
                    if truck.has_capacity():
                        truck.load_package(copy(package))
                        self._checkout_package(package)
                already_used.append(i)

    def _generate_views(self) -> None:
        def _add_special_handling(p: Package) -> None:
            if p.has_delay():
                self._delayed.append(copy(p))
            if p.has_dependency() is not None:
                deps = self._find_dependencies(p)
                for dep in deps:
                    if dep not in self._dependencies:
                        self._dependencies.append(copy(dep))
                if p not in self._having_dependency:
                    self._having_dependency.append(copy(p))
            if p.has_invalid_flag():
                self._invalid.append(copy(p))
            if p.has_priority():
                self._priority.append(copy(p))
            if not (p.has_delay()
                    or p.has_dependency()
                    or p.has_invalid_flag()
                    or p.has_priority()
                    or p.has_truck_requirement()):
                self._standard.append(copy(p))

        def _print_stats():
            print(f'\n{Style.END}{Style.RED1}{len(self._invalid)}{Style.END} packages with an invalid address.')
            print(f'{Style.END}{Style.RED1}{len(self._having_dependency)}{Style.END} having dependencies.')
            print(f'{Style.END}{Style.YELLOW2}{len(self._dependencies)}{Style.END} which are dependencies.')
            print(f'{Style.END}{Style.YELLOW2}{len(self._delayed)}{Style.END} packages arriving late.')
            print(f'{Style.END}{Style.BLUE1}{len(self._priority)}{Style.END} with priority.')
            print(f'{Style.END}{Style.GREEN1}{len(self._standard)}{Style.END} with no special handling.\n')
            print('Done.')

        from WGUPS.cli.environment import progress, cls
        print(f'Computing special handling for: {len(self._packages)} packages')
        for package in progress(self._packages):
            _add_special_handling(package)

        _print_stats()
        input(f'Press <{Style.RED1}Enter{Style.END}> to continue ...\n{Style.GREEN2}> {Style.END}')
        cls()

    def _update_remaining(self):
        for package in self._packages:
            if package not in self._delivered and package not in self._enroute:
                self._remaining.add(copy(package))
            if package in self._enroute and package in self._delivered:
                self._enroute.remove(package)

    def _dispatch_trucks(self):

        # keep track of which packages went on which trucks
        delivery_book: dict[int, list[list[Package]]] = dict()
        while self._remaining:
            for truck in self._trucks:
                plan = self._trucks[0].optimize_delivery(_graph=self._graph, _hub=self.HUB)

    def _checkout_package(self, p: Package) -> None:
        # move the package from the remaining pool to enroute
        if p in self._remaining:
            self._remaining.remove(p)
        self._enroute.add(copy(p))
        # remove the package from any views it's contained in
        if p in self._dependencies:
            self._dependencies.remove(p)

        if p in self._delayed:
            self._delayed.remove(p)

        if p in self._having_dependency:
            self._having_dependency.remove(p)

        if p in self._invalid:
            self._invalid.remove(p)

        if p in self._priority:
            self._priority.remove(p)

        if p in self._standard:
            self._standard.remove(p)

    def snapshot(self) -> str:
        pass
