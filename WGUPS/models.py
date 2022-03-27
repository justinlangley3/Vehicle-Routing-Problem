from __future__ import annotations

# Standard Library
import datetime
import inspect
from collections import namedtuple
from dataclasses import dataclass, field
from enum import Enum, auto
from itertools import count

# Project Imports
from adt import HashTable


@dataclass(eq=True, order=True, unsafe_hash=False, frozen=True)
class Address:
    name: str
    street: str
    city: str
    state: str
    postal: str

    def __str__(self) -> str:
        return f'{self.street}, {self.city}, {self.state}, {self.postal}'

    def __iter__(self):
        members = [attr for attr in dir(Address) if not callable(getattr(Address, attr)) and not attr.startswith("__")]
        print(members)
        for member in members:
            yield self.__getattribute__(member)
        raise StopIteration

    def __next__(self):
        return self


@dataclass(eq=True)
class Package:
    # class vars
    id: int
    address: Address
    location: Coordinate
    deadline: datetime
    mass: float
    notes: str
    delivered: datetime
    status: PackageStatus
    pos: int

    def get_status(self):
        return self.status.value


class PackageStatus(Enum):
    Hub = "hub"
    Enroute = "enroute"
    Delivered = "delivered"


@dataclass()
class Truck:
    packages: HashTable

    def all_packages(self) -> list:
        as_list = list()
        for bucket in self.packages:
            as_list.extend(bucket)
        return as_list

    def compute_delivery_order(self) -> list:
        return


@dataclass(eq=True, order=True, frozen=True)
class Coordinate:
    lat: float = 0.0
    long: float = 0.0
