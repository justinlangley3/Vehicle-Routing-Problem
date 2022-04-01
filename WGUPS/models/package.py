from __future__ import annotations

# STL Imports
import datetime
from dataclasses import dataclass
from time import time
from enum import Enum

# Project Imports
import WGUPS.util.time
from WGUPS.models.address import Address
from WGUPS.util.strings import tokenize, find_token, unpack_token


@dataclass(eq=True, order=True)
class Package:
    # class vars
    id: int
    address: Address
    deadline: time
    mass: float
    notes: str
    status: PackageStatus
    delivered: datetime

    has_update = False
    arrival: datetime.time = datetime.time()

    def __post_init__(self):
        self.delivered += datetime.timedelta(hours=8, minutes=0, milliseconds=0, microseconds=0)

    def __hash__(self) -> int:
        """
        Required so that packages are hashable.
        Simply returns its id, since they are the only thing unique

        Returns: int

        """
        return self.id

    def get_status(self) -> PackageStatus:
        """
        Retrieves the value of this package's status enum

        Returns: status

        """
        return self.status.value

    def set_status(self, status: PackageStatus) -> None:
        """
        Used for updating package statuses
        Args:
            status: a PackageStatus enum value

        Returns: None

        """
        self.status = status

    def has_delay(self) -> datetime.time | None:
        """
        Checks if a package is a late arrival.

        Tokenizes data held in notes,
        then parses out arrival time if the 'arrival=' key is present

        Returns: time | None

        """
        token = find_token(string=self.notes, key='arrival')
        if token is None:
            return None
        else:
            value = unpack_token(token=token, delimited=True)
            from WGUPS.util.time import time_from_string
            return time_from_string(value)

    def has_dependency(self) -> list[int] | None:
        """
        Checks if a package has dependencies.
        If there are dependencies, they are returned in a list

        Returns: list[int] or None

        """
        from WGUPS.util.strings import tokenize
        if len(self.notes) > 0:
            tokens = tokenize(self.notes)
            for token in tokens:
                key = 'dep='
                if key in token:
                    values = unpack_token(token)
                    if len(values) == 0:
                        return None
                    elif len(values) == 1:
                        return [int(values)]
                    else:
                        return [int(value) for value in values.split(sep=',')]
        return None

    def has_invalid_flag(self) -> bool | None:
        """
        Determines if a package has its address indicated as invalid by its notes
        Returns: bool or None

        """
        token = find_token(string=self.notes, key='ADDRESS_INVALID')
        if token is None:
            return False
        else:
            return True

    def has_priority(self) -> bool:
        """
        Determines if a package has a priority requirement

        Returns:

        """
        if datetime.time(8, 0) < self.deadline < datetime.time(23, 59, 59, 999999):
            return True
        return False

    def printable(self) -> str:
        """
        Makes a printable row containing this package's properties
        Returns: str

        """
        def _make_row(_props: tuple[str, ...], _widths: tuple[int, ...], _style: str, _tab: int = 2) -> str:
            from WGUPS.util import padr
            _row = ''
            for _i, _prop in enumerate(_props):
                _row += ' ' * _tab
                if len(_prop) <= _widths[_i]:
                    _prop = padr(string=_prop, count=(_widths[_i] - len(_prop)))
                    _prop = f'{_style}{_prop}{Style.END}'
                    _row += _prop
                else:
                    _trim = _widths[_i] - 3
                    _prop = _prop[:_trim] + '...'
                    _prop = f'{_style}{_prop}{Style.END}'
                    _row += _prop
            return _row

        from WGUPS.cli.style import Style
        from WGUPS.util.time import to_digital_clock

        # _cols = ('ID', 'Street', 'City', 'State', 'Zip', 'Mass (kg)' 'Status')
        widths = (2, 38, 16, 5, 5, 9, 17)

        props = (str(self.id),
                 self.address.street,
                 self.address.city,
                 self.address.state,
                 self.address.postal,
                 str(self.mass),
                 str(self.status.value),
                 to_digital_clock(self.delivered))

        if self.status == PackageStatus.Delivered:
            # color code delivered packages in green, include delivered time
            return _make_row(_props=props, _widths=widths, _style=Style.GREEN1)
        if self.status == PackageStatus.Enroute:
            # color code enroute packages in yellow, exclude delivered time
            return _make_row(_props=props[:-1], _widths=widths[:-1], _style=Style.YELLOW2)
        if self.status == PackageStatus.Hub:
            # color code in hub packages in red, exclude delivered time
            return _make_row(_props=props[:-1], _widths=widths[:-1], _style=Style.RED1)

    def has_truck_requirement(self) -> int | None:
        """
        Checks if a package requires the use of a specific truck
        If a specific truck is required, its id is returned

        Returns: int or None

        """

        if len(self.notes) > 0:
            tokens = tokenize(self.notes)
            for token in tokens:
                if 'truck=' in token:
                    truck = unpack_token(token)
                    return int(truck)
        return None


class PackageStatus(Enum):
    Hub = "hub"
    Enroute = "enroute"
    Delivered = "delivered"
