# STL Imports
from dataclasses import dataclass, field

# Project Imports
from WGUPS.models import Address
from WGUPS.models.package import Package, PackageStatus
from WGUPS.structures.graph import Graph


@dataclass()
class Truck:
    _id: int
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

    def __hash__(self):
        return self._id

    @property
    def truck_id(self) -> int:
        return self._id

    @property
    def speed(self) -> int:
        return self._speed

    @property
    def packages(self) -> list[Package]:
        return self._packages

    @property
    def pids(self) -> list[int]:
        return self._pids

    def load_package(self, package):
        if self.is_full():
            raise TruckCapacityError
        for loaded in self._packages:
            if package.id == loaded.id:
                raise AlreadyOnTruckError
        package.set_status(PackageStatus.Enroute)
        self._packages.append(package)
        self._pids.append(package.id)

    def is_full(self) -> bool:
        return len(self._packages) == self._capacity

    def capacity_remaining(self) -> int:
        if self.is_full():
            return 0
        return self._capacity - len(self._packages)

    def optimize_delivery(self, _graph: Graph, _hub: Address) -> list[Address]:
        from WGUPS.core import tsp
        solver = tsp.Solver(use=tsp.Method.ConvexHull, graph=_graph, packages=self.packages, hub=_hub)
        optimized = solver.solve()
        return optimized

    def clear(self):
        self._pids.clear()
        self._packages.clear()


class TruckCapacityError(Exception):
    """Raised when the truck is full, but load_package() was attempted"""
    pass


class AlreadyOnTruckError(Exception):
    """Raised when the truck is full, but load_package() was attempted"""
    pass
