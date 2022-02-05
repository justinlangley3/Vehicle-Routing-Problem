import datetime

__EOD__: str = '17:00'


def get_EOD():
    return __EOD__


def set_EOD(time: str):
    global __EOD__
    __EOD__ = time


class Package:
    # class vars
    id_val: int
    street_val: str
    city_val: str
    state_val: str
    postal_val: str
    deadline_val: datetime
    mass_val: float
    notes_val: str
    load_pos: int

    # magic methods
    def __init__(self, values: list):
        assert len(values) == 8
        # set private vars
        self._date = datetime.date.today()
        # Set instance vars if provided
        self.id_val = int(values[0])
        self.street_val = values[1]
        self.city_val = values[2]
        self.state_val = values[3]
        self.postal_val = values[4]
        if values[5] == 'EOD':
            self.deadline_val = datetime.datetime.strptime(f'{self._date} {__EOD__}', '%Y-%m-%d %H:%M')
        else:
            self.deadline_val = datetime.datetime.strptime(f'{self._date} {self.convert12(values[5])}', '%Y-%m-%d %H:%M')
        self.mass_val = float(values[6])
        self.notes_val = values[7]
        self.load_pos = -1

    def __repr__(self):
        return f"Package(id={repr(self.id_val)}, street={repr(self.street_val)}, city={repr(self.city_val)}, " \
               f"state={repr(self.state_val)}, postal={repr(self.postal_val)}, deadline={repr(self.deadline_val)}, " \
               f"mass={repr(self.mass_val)}, notes={repr(self.notes_val)}"

    def __str__(self):
        # join all instance variable with comma separator
        return ','.join((str(self.id_val), self.street_val, self.city_val, self.state_val, self.postal_val,
                         str(self.deadline_val), str(self.mass_val), self.notes_val))

    # getter properties
    @property
    def city(self) -> str:
        return self.city_val

    @property
    def deadline(self) -> str:
        return self.deadline_val.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def mass(self) -> float:
        return self.mass_val

    @property
    def notes(self) -> str:
        return self.notes_val

    @property
    def position(self) -> int:
        return self.load_pos

    @property
    def postal(self) -> str:
        return self.postal_val

    @property
    def state(self) -> str:
        return self.state_val

    @property
    def street(self) -> str:
        return self.street_val

    @property
    def package_id(self) -> int:
        return self.id_val

    # setter properties
    @city.setter
    def city(self, c: str) -> None:
        self.city_val = c

    @deadline.setter
    def deadline(self, d: str) -> None:
        self.deadline_val = datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')

    @mass.setter
    def mass(self, m: float) -> None:
        self.mass_val = m

    @notes.setter
    def notes(self, n: str) -> None:
        self.notes_val = n

    @package_id.setter
    def package_id(self, pkg_id: int) -> None:
        assert (pkg_id >= 0)
        self.id_val = pkg_id

    @position.setter
    def position(self, pos: int) -> None:
        assert pos > -1
        self.load_pos = pos

    @postal.setter
    def postal(self, p: str) -> None:
        self.postal_val = p

    @state.setter
    def state(self, s: str) -> None:
        self.state_val = s

    @street.setter
    def street(self, s: str) -> None:
        self.street_val = s

    @staticmethod
    def convert12(s: str) -> str:
        if s[-2:] == 'AM':
            return s[:-3]
        if s[-2:] == 'PM':
            h = str(int[:2] + 12)
            return h + s[2:-3]


class Truck:
    def __init__(self):
        self.packages = list[Package]

    def _get_delivery_order(self):
        # TODO: call a method in the graph data structure here
        # this method should find an optimal delivery route, and assign a position to each package

        self.packages = sorted(self.packages, key=lambda package: package.position)
        return
