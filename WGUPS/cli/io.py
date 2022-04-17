# STL
from pathlib import Path

# Project Imports
from WGUPS.core import Ruler
from WGUPS.models import Address, Coordinate, Package
from WGUPS.structures import Graph, HashTable
# Package Imports
from .environment import cls
from .style import Style


def get_last_folder_in_path(path: str) -> str:
    """
    Trims a path to the last 'leaf/folder/directory' in the path

    Use case:
      If a folder is appropriately named then the folder name can be used in the CLI to prompt file input

      A folder named 'GPS' could result in a prompt that says: Please select a GPS file:.
      Alternatively, a prompt could read: Please select a file from the GPS folder:

    Output Examples:
        'C:\\Users\\name\\Documents\\new_folder -> new_folder'
        '/home/user/documents/new_folder -> new_folder'
    Note: This works whether the path is terminated in either type of slash
    """
    # trim path to the last folder
    folders = path.split(sep='/')
    folder = folders.pop()
    # check if the 'folder' is an empty string
    if folder == '':
        # path was terminated by a slash resulting in an empty string here
        # simply pop the next item to get the 'folder'
        return folders.pop()
    return folder


def get_file_properties(file: Path) -> tuple[str, ...]:
    """
    Retrieve metadata about the file

    This method should technically call stat() or lstat() on the file.
    However, handling every cross-platform difference is a lot
    to do for the scope of this project.

    os.getmtime() is guaranteed to retrieve the last modified time on any OS

    Returns a tuple of name, extension, last modified time
    """
    from os.path import getmtime
    from time import strftime, localtime
    modified = strftime("%Y-%m-%d %H:%M:%S", localtime(getmtime(file)))
    return file.stem, file.suffix, modified


def request_data_files(relative_paths: list[str], ext: str) -> tuple[Path, ...]:
    def _build_directories(_dirs: list[str]) -> list[list[Path]]:
        """
        Build a listing of all files located at each path provided
        """
        from .environment import ls
        _listing: list[list[Path]] = list()
        for _directory in _dirs:
            _items = ls(path=_directory, ext=ext)
            _listing.append(_items)
        return _listing

    def _make_row(_cols: tuple[str, ...], _col_widths: tuple[int, ...], _styles: tuple[str, ...],
                  _tab_size: int = 2) -> str:
        _row = ''
        try:
            # all tuples must be the same length for formatting to be applied appropriately
            assert len(_cols) == len(_styles) and len(_cols) == len(_col_widths)

            # format and style the columns since the assertion passed
            for _i, _col in enumerate(_cols):
                # tab the column over
                _row += ' ' * _tab_size
                # check if data fits in the given width
                if len(_col) <= _col_widths[_i]:
                    # pad extra spaces until the width is filled
                    from WGUPS.util import padr
                    _row += f'{_styles[_i]}' + padr(string=_col, count=(_col_widths[_i] - len(_col)))
                else:
                    # show as much data as can fit
                    _trim = _col_widths[_i] - 3
                    _row += f'{_styles[_i]}' + _col[:_trim] + '...'
                _row += f'{Style.END}'
            _row += '\n'
            return _row
        except AssertionError:
            pass

    def _tabulate_props(_paths: list[Path]) -> str:
        """Formats columnar data into a table to print"""
        _table = ''
        _rows: list[str] = list()

        # Specify columns, column widths, and styling
        _cols = ('#:', 'File', ' Ext', 'Last Modified')
        _widths = (2, 36, 4, 19)
        _styles = (Style.BOLD, Style.BLUE1, Style.BLUE1, Style.YELLOW2)

        # create table header
        _fill = '-' * 68
        _separator = f'{Style.GREY}+{_fill}+{Style.END}\n'
        _header = _make_row(_cols=_cols, _col_widths=_widths, _styles=_styles)
        _header = _separator + _header + _separator
        _table += _header

        # generate columns
        for _i, _path in enumerate(_paths):
            _opt = str(_i) + ':'
            _name, _ext, _modified = get_file_properties(_path)
            _props = (_opt, _name, _ext, _modified)
            _new_row = _make_row(_cols=_props, _col_widths=_widths, _styles=_styles)
            _rows.append(_new_row)

        # build the table
        for _row in _rows:
            _table += _row

        return _table

    def _prompt_user(_listing: list[Path], _folder: str) -> Path:
        """
        Prompt the user to select one of the files presented.
        Returns their selection as a path
        """
        # build the prompt
        table = _tabulate_props(listing)
        prompt = f'Please select a {Style.RED1}{_folder}{Style.END} file:\n' \
                 f'{table}\n' \
                 f'{Style.GREEN1}> {Style.END}'

        # get the selection and return the file path
        from .prompts import choose_int
        choice = choose_int(prompt=prompt, count=len(listing))
        cls()
        return listing[choice]

    folders = [get_last_folder_in_path(path) for path in relative_paths]
    listings = _build_directories(relative_paths)
    selections = list()
    for i, listing in enumerate(listings):
        new_selection = _prompt_user(_listing=listing, _folder=folders[i])
        selections.append(new_selection)
    return tuple(selections)


def _parse_csv(path: Path):
    """
    Parses out a csv file into a list
    :param path: str, the file location
    :return: list
    """
    try:
        from csv import reader
        with open(path, mode='r', encoding='utf-8-sig') as csvfile:
            reader = reader(csvfile, dialect='excel')
            return list(reader)
    except IOError as _:
        print(f'File: {path}, was unable to be opened or does not exist.')


def _load_address(address_data: list[str], coordinate: Coordinate) -> Address:
    """Builds an address object"""
    name = address_data[0]
    street = address_data[1]
    city = address_data[2]
    state = address_data[3]
    postal = address_data[4]
    return Address(name=name,
                   street=street,
                   city=city,
                   state=state,
                   postal=postal,
                   coordinate=coordinate)


def build_packages(path: Path, addresses: list[Address]) -> HashTable[int, Package]:
    """Reads in csv data and performs setup on hash table data structure for holding packages"""
    def lookup_address(container: list[Address], key: list[str]) -> Address | None:
        for address in container:
            members = [address.name, address.street, address.city, address.state, address.postal]
            if key == members:
                return address
            # TODO: implement way for user to correct & retry or else skip for junk data
        return None

    packages: HashTable[int, Package] = HashTable()
    lines = _parse_csv(path)[1:]
    print(f'Building{Style.END} {Style.RED1}{Style.UNDERLINE}Packages{Style.END}')
    from WGUPS.cli.environment import progress
    for row in progress(lines):
        package_id = int(row[0])
        address_data = row[1:6]
        package_address = lookup_address(container=addresses, key=address_data)

        package_data = row[-3:]

        from WGUPS.util.time import datetime_from_string
        package_deadline = datetime_from_string(package_data[0])

        package_mass = int(package_data[1])
        package_notes = package_data[2]

        from WGUPS.models import PackageStatus
        new_package = Package(id=package_id,
                              address=package_address,
                              mass=package_mass,
                              notes=package_notes,
                              status=PackageStatus.Hub,
                              _deadline=package_deadline,
                              _delivered=None
                              )
        # TODO: implement safe hashing for packages, so handling for updating package data can be implemented
        #       note: this may not be needed if the id is placed in the hashtable as the key
        #             in this case the underlying object could change, but its hash remains the same
        packages[package_id] = new_package

    input(f"{Style.END}\nDone.\n"
          f"Press <{Style.RED1}Enter{Style.END}>"
          f" to continue ...\n{Style.GREEN2}> {Style.END}")
    cls()
    return packages


def build_graph(path: Path) -> tuple[Graph[Address], list[Address]]:
    """Reads in distance data and performs setup on the graph data structure"""
    #
    # Helper methods
    #
    def load_location(coords: list[str]) -> Coordinate:
        """
        Creates a Coordinate object.
        Valid Input:
          - A list slice containing a latitude, longitude
            Note: order matters, latitude must come first
        """
        latitude, longitude = float(coords[0]), float(coords[1])
        return Coordinate(lat=latitude, long=longitude)

    def parse_gps_data(p: Path) -> list[Address]:
        processed: list[Address] = list()
        lines = _parse_csv(p)[1:]

        for i, row in enumerate(lines):
            address_data = row[0].replace('\n', '').split(sep=',')
            coordinate = load_location(row[1:])
            new_address = _load_address(address_data=address_data, coordinate=coordinate)
            processed.append(new_address)
        return processed

    #
    # Data Processing
    #
    addresses = parse_gps_data(path)
    new_graph: Graph[Address] = Graph()
    new_ruler = Ruler(unit=Ruler.Units.Miles, calc_method=Ruler.calc_method.Vincenty)

    from WGUPS.cli.environment import progress
    print(f'Processing{Style.END} {Style.RED1}{Style.UNDERLINE}Locations{Style.END}\n')
    # add all vertices
    print('Computing addresses')
    for address in progress(addresses):
        new_graph.add_vertex(address)
    print(f'{Style.GREEN1}  {new_graph.vertex_sum()} addresses.{Style.END}\n')

    # add all edges
    print('Computing connections')
    for source in progress(it=addresses, steps=len(addresses) ** 2):
        for destination in addresses:
            distance = new_ruler.compute_distance(source.coordinate, destination.coordinate)
            new_graph.add_edge(source, destination, distance)
    print(f'{Style.GREEN1}  {new_graph.edge_sum()} connections.{Style.END}\n')
    input(f"Done.\n"
          f"Press <{Style.RED1}Enter{Style.END}> to continue ..."
          f"\n{Style.GREEN2}> {Style.END}")
    cls()
    return new_graph, addresses
