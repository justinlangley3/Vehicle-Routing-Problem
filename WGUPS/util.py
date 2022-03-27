# STL
import csv
import pathlib
import sys

# Project packages
import adt
import ruler
from models import Address, Coordinate, Package, PackageStatus


def get_platform() -> str:
    platforms = {
        'linux1': 'Linux',
        'linux2': 'Linux',
        'darwin': 'OS X',
        'win32': 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform

    return platforms[sys.platform]


def str_to_chars(s: str) -> list[str]:
    return [c for c in s]


def parse_csv(path: pathlib.Path):
    """
    Parses out a csv file into a list
    :param path: str, the file location
    :return: list
    """
    try:
        with open(path, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile, dialect='excel')
            return list(reader)
    except IOError as _:
        print(f'File: {path}, was unable to be opened or does not exist.')


# calls parse_csv() on the path and modifies the returned data to create lists of vertices and edges
def parse_distance_data(path) -> (list, list):
    lines = parse_csv(path)

    # vertices are the addresses contained in the csv header
    v = [i.split(',\n')[1] for i in lines[0][1:]]

    # edges are represented by the weights at the column, row intersection
    # we also only care about non-null entries, so the lambda ignores things like ',,,'
    e = [list(filter(lambda x: x != "", line[1:])) for line in lines[1:]]

    return v, e


def _load_address(data: list[str]) -> Address:
    a, b, c, d, e = data[0], data[1], data[2], data[3], data[4]
    return Address(name=a, street=b, city=c, state=d, postal=e)


# calls parse_csv() on the path, creates packages from the data, and inserts them into a HashTable


def parse_package_data(path,
                       addresses: dict[Address, Coordinate]
                       ) -> structures.HashTable[int, Package]:
    import time

    time_fmt = '%H:%M'

    def make_time(t: str) -> time:
        # split time passed in into tokens that can be processed individually
        def tokenize(timestr: str):
            _am_pm = timestr.split(sep=' ')[1]
            timestr = timestr[0:-3]
            _h = timestr.split(sep=':')[0]
            _m = timestr.split(sep=':')[1]
            return _h, _m, _am_pm

        # handle pm time (+12 hours)
        def handle_pm(h):
            return str(int(h) + 12)

        # parse time from hours, minutes
        def build(h, m):
            return time.strptime(h + ':' + m, time_fmt)

        # return default time for end of business day if 'EOD' is passed in
        if 'eod' in t.lower():
            return build('17', '00')

        # tokenize time passed in and format to 24hr time format
        hours, minutes, am_pm = tokenize(t)
        if 'am' in am_pm.lower():
            return build(hours, minutes)
        if 'pm' in am_pm.lower():
            hours = handle_pm(hours)
            return build(hours, minutes)

    def lookup_address(container: dict[Address, Coordinate],
                       key: list[str]
                       ) -> tuple[Address, Coordinate] | None:
        item = _load_address(key)
        for k, v in container.items():
            if item == k:
                return k, v
        return None

    table = structures.HashTable()
    lines = parse_csv(path)[1:]
    for row in lines:
        pid = row[0]
        address_data = row[1:6]
        a, b = lookup_address(container=addresses, key=address_data)

        package_data = row[-3:]
        c = make_time(package_data[0])
        d = int(package_data[1])
        e = package_data[2]

        new_package = Package(id=pid,
                              address=a,
                              location=b,
                              deadline=c,
                              mass=d,
                              notes=e,
                              delivered=None,
                              status=PackageStatus.Hub,
                              pos=-1
                              )
        table.put(key=pid, value=new_package)
    return table


def parse_gps_data(path) -> dict[Address, Coordinate]:
    def load_location(coords: list[str]) -> Coordinate:
        latitude, longitude = float(coords[0]), float(coords[1])
        return Coordinate(lat=latitude, long=longitude)

    addresses = dict()
    lines = parse_csv(path)[1:]

    for i, row in enumerate(lines):
        address = row[0].replace('\n', '').split(sep=',')
        new_address = _load_address(address)
        new_location = load_location(row[1:])
        addresses[new_address] = new_location

    return addresses


def build_graph(addresses: dict[Address, Coordinate]):
    from adt import Graph

    new_graph: Graph[Address] = Graph()
    new_ruler = ruler.Ruler(unit=ruler.Ruler.Units.Miles)

    # add all vertices
    for address in addresses.keys():
        new_graph.add_vertex(address)

    # add all edges
    for current_address, current_location in addresses.items():
        for address, location in addresses.items():
            distance = new_ruler.compute_distance(current_location, location)
            new_graph.add_edge(current_address, address, distance)
    return new_graph
