# STL Imports
import datetime
import pprint
from dataclasses import dataclass, field

# Project Imports
from WGUPS.models import Address
from WGUPS.models.package import Package, PackageStatus
from WGUPS.structures.graph import Graph


@dataclass()
class Truck:
    _pids: list[int] = field(default_factory=list)
    _packages: list[Package] = field(default_factory=list)
    _capacity: int = 16
    _fuel: float = float('inf')
    _speed: int = 18

    def __iter__(self):
        for package in self._packages:
            yield package

    def __next__(self):
        pass

    def load_package(self, package):
        if self.is_full():
            raise TruckCapacityError
        package.set_status(PackageStatus.Enroute)
        self._pids.append(package.id)
        self._packages.append(package)

    def is_full(self) -> bool:
        return len(self._packages) == self._capacity

    def has_capacity(self) -> int | None:
        if len(self._packages) < self._capacity:
            return self._capacity - len(self._packages)
        return None

    def optimize_delivery(self, _graph: Graph, _hub: Address) -> list[Package]:
        from WGUPS.core import tsp
        solver = tsp.Solver(use=tsp.Method.ConvexHull, graph=_graph, packages=self.packages, hub=_hub)
        optimized = solver.solve()
        return optimized

    def perform_delivery(self, _path: list[Address], _graph: Graph, departure: datetime.time):
        def _calc_distances(_path: list[Address]) -> tuple[int, list[tuple[Address, Address, float]]]:
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
            _total = 0
            _prev_point = _path[0]
            _path.remove(_prev_point)
            while _path:
                _current = _path[0]
                _edge = (_prev_point, _current, _graph[_prev_point][_current])
                _seen.append(_edge)
                _prev_point = _current
                _path.remove(_current)
            for _distance in _seen:
                _total += _distance[2]
            return _total, _seen

        # call subroutine to calculate distances
        total_distance, edges = _calc_distances(_path=_path)

        # update package statuses
        for edge in edges:
            from WGUPS.util.time import calc_travel_time
            h, m, s = calc_travel_time(edge[2], self._speed)

        pass

    @property
    def packages(self) -> list[Package]:
        return self._packages


class TruckCapacityError(Exception):
    """Raised when the truck is full, but load_package() was attempted"""
    pass
