from __future__ import annotations

# Standard Library
from dataclasses import dataclass
from enum import Enum, auto

# Project Imports
from WGUPS.models.address import Coordinate

_EARTH_SEMI_MAJOR = 6378137.0
_EARTH_SEMI_MINOR = 6356752.314245


# noinspection NonAsciiCharacters,PyPep8Naming,SpellCheckingInspection
@dataclass()
class Ruler:
    class Method(Enum):
        Haversine = auto()
        Euclidean = auto()
        Vincenty = auto()

    class Units(Enum):
        Feet = 'ft'
        Kilometers = 'km'
        Meters = 'm'
        Miles = 'mi'
        Yards = 'yd'

    calc_method: Method = Method.Haversine
    unit: Units = Units.Meters

    def units(self, new: Ruler.Units = None) -> Ruler.Units:
        if new:
            self.unit = new
        return self.unit

    def method(self, new: Ruler.Method) -> Ruler.Method:
        if new:
            self.calc_method = new
        return self.calc_method

    def compute_distance(self, c1: Coordinate, c2: Coordinate, precision: int = 1, as_str: bool = False):
        match self.calc_method:
            case Ruler.Method.Haversine:
                meters = self._haversine(c1, c2)
            case Ruler.Method.Euclidean:
                meters = self._euclidean(c1, c2)
            case Ruler.Method.Vincenty:
                meters = self._vincenty(c1, c2)
            case _:
                meters = self._haversine(c1, c2)

        d = self._convert_units(meters, precision)
        if as_str:
            return self._distance_to_str(d)
        return d

    def _distance_to_str(self, d: float) -> str:
        return f'{d} {self.unit.value}'

    def _convert_units(self, d: float, precision: int):
        match self.unit:
            case Ruler.Units.Kilometers:
                d *= 0.001
            case Ruler.Units.Miles:
                d *= 0.000621371
            case Ruler.Units.Feet:
                d *= 3.28084
            case Ruler.Units.Yards:
                d *= 1.09361
            case _, Ruler.Units.Meters:
                pass
        d = round(d, precision)
        return d

    @staticmethod
    def orientation(p: Coordinate, q: Coordinate, r: Coordinate):
        """
        Orientation of ordered triplet algorithm
        0 -> collinear
        1 -> clockwise
        2 -> counter-clockwise
        """
        import math

        val = math.radians(q.lat - p.lat) * math.radians(r.long - q.long)
        val -= math.radians(q.long - p.long) * math.radians(r.lat - q.lat)
        if val == 0:
            return 0
        elif val > 0:
            return 1
        else:
            return 2

    # distance between two points on a plane, ignores Earth's curvature (inaccurate)
    @staticmethod
    def _euclidean(c1: Coordinate, c2: Coordinate):
        import math

        def distance_long(lat_a, long_a, long_b):
            return (long_b - long_a) * math.cos(lat_a)

        def distance_lat(lat_a, lat_b):
            return lat_b - lat_a

        # calculate mean Earth radius in m
        R = 0.5 * (_EARTH_SEMI_MAJOR + _EARTH_SEMI_MINOR)

        # unit conversion in meters
        meters = (2 * math.pi * R) / 360

        # calculate pythagorean distance between the two points
        d = math.sqrt(
            distance_long(c1.lat, c2.long, c2.long) ** 2
            + distance_lat(c1.lat, c2.lat) ** 2
        )
        # apply the unit conversion
        d *= meters
        return d

    # adaptation of spherical law of cosines for distance of spherical triangles (more accurate)
    @staticmethod
    def _haversine(c1: Coordinate, c2: Coordinate):
        import math
        # calculate mean radius of Earth in m
        R = 0.5 * (_EARTH_SEMI_MAJOR + _EARTH_SEMI_MINOR)

        # convert degree-decimal coordinates to radians
        ??a, ??b = math.radians(c1.lat), math.radians(c2.lat)
        ??a, ??b = math.radians(c1.long), math.radians(c2.long)

        # change in latitude (north-south), longitude (east-west)
        ????, ???? = (??b - ??a), (??b - ??a)

        # haversine formula
        t = math.sin(???? / 2) ** 2
        t += math.cos(??a) * math.cos(??b) * (math.sin(???? / 2) ** 2)
        d = 2 * R * math.asin(math.sqrt(t))
        return d

    # improvements upon haversine that accounts for Earth's 'flattening' i.e. it's equatorial bulge (most accurate)
    # the Newtonian approximation may fail to converge if ?? is initially greater than ?? in absolute value
    @staticmethod
    def _vincenty(c1: Coordinate, c2: Coordinate):
        import math

        # Earth Major/Minor axis (in meters), and 'flattening' ratio
        a = _EARTH_SEMI_MAJOR
        b = _EARTH_SEMI_MINOR
        ?? = 1 / 298.257223563

        # approx. 0.06mm of accuracy, defines when to stop iterating
        ?? = 1e-12

        # assume coordinate data is in deg, and appropriately convert to radians
        ??a, ??b = math.radians(c1.lat), math.radians(c2.lat)
        ??a, ??b = math.radians(c1.long), math.radians(c2.long)

        # reduced latitudes defined by the 'flattening' of Earth
        U1 = math.atan((1 - ??) * math.tan(??a))
        U2 = math.atan((1 - ??) * math.tan(??b))

        # delta lambda (difference between longitude of a and longitude of b)
        ???? = ??b - ??a

        ?? = ???? + 0

        while True:
            t = (math.cos(U2) * math.sin(??)) ** 2
            t += (math.cos(U1) * math.sin(U2) - math.sin(U1) * math.cos(U2) * math.cos(??)) ** 2
            sin?? = t ** 0.5
            cos?? = math.sin(U1) * math.sin(U2) + math.cos(U1) * math.cos(U2) * math.cos(??)
            ?? = math.atan2(sin??, cos??)

            if sin?? == 0:   # points are coincident, avoid divide by zero
                return 0.0
            sin?? = (math.cos(U1) * math.cos(U2) * math.sin(??)) / sin??
            cos_sq_?? = 1 - sin?? ** 2
            cos2??m = cos?? - 2 * math.sin(U1) * math.sin(U2) / cos_sq_??
            C = ?? * cos_sq_?? * (4 + ?? * (4 - 3 * cos_sq_??)) * 0.0625

            t = ?? + C * sin?? * (cos2??m + C * cos?? * (-1 + 2 * cos2??m ** 2))
            L = ???? + (1 - C) * ?? * sin?? * t

            if abs(L - ??) <= ??:
                break
            else:
                ?? = L

        # performed once lambda is within the desired degree of accuracy
        u_sq = cos_sq_?? * ((a ** 2 - b ** 2) / b ** 2)
        A = 1 + (u_sq * (4096 + u_sq * (-768 + u_sq * (320 - 175 * u_sq)))) / 16384
        B = u_sq * (256 + u_sq * (-128 + u_sq * (74 - 47 * u_sq))) / 1024

        t = cos2??m + 0.25 * B * (cos?? * (-1 + 2 * cos2??m ** 2))
        t -= (B * cos2??m / 6) * (-3 + 4 * math.sin(??) ** 2) * (-3 + 4 * cos2??m ** 2)
        ???? = B * sin?? * t
        s = b * A * (?? - ????)

        return s
