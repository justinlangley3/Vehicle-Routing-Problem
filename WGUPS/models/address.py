from __future__ import annotations

# STL Imports
from dataclasses import dataclass


@dataclass(eq=True, order=True, unsafe_hash=False, frozen=True)
class Address:
    name: str
    street: str
    city: str
    state: str
    postal: str
    coordinate: Coordinate

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


@dataclass(eq=True, order=True, frozen=True)
class Coordinate:
    lat: float = 0.0
    long: float = 0.0
