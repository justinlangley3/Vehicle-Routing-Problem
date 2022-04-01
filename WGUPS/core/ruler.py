from __future__ import annotations

# Standard Library
from dataclasses import dataclass
from enum import Enum, auto

# Project Imports
from WGUPS.models.address import Coordinate

_EARTH_SEMI_MAJOR = 6378137.0
_EARTH_SEMI_MINOR = 6356752.314245


# noinspection NonAsciiCharacters
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
        ϕa, ϕb = math.radians(c1.lat), math.radians(c2.lat)
        λa, λb = math.radians(c1.long), math.radians(c2.long)

        # change in latitude (north-south), longitude (east-west)
        Δϕ, Δλ = (ϕb - ϕa), (λb - λa)

        # haversine formula
        t = math.sin(Δϕ / 2) ** 2
        t += math.cos(ϕa) * math.cos(ϕb) * (math.sin(Δλ / 2) ** 2)
        d = 2 * R * math.asin(math.sqrt(t))
        return d

    # improvements upon haversine that accounts for Earth's 'flattening' i.e. it's equatorial bulge (most accurate)
    # the Newtonian approximation may fail to converge if λ is initially greater than π in absolute value
    @staticmethod
    def _vincenty(c1: Coordinate, c2: Coordinate):
        import math

        # Earth Major/Minor axis (in meters), and 'flattening' ratio
        a = _EARTH_SEMI_MAJOR
        b = _EARTH_SEMI_MINOR
        ƒ = 1 / 298.257223563

        # approx. 0.06mm of accuracy, defines when to stop iterating
        ε = 1e-12

        # assume coordinate data is in deg, and appropriately convert to radians
        ϕa, ϕb = math.radians(c1.lat), math.radians(c2.lat)
        λa, λb = math.radians(c1.long), math.radians(c2.long)

        # reduced latitudes defined by the 'flattening' of Earth
        U1 = math.atan((1 - ƒ) * math.tan(ϕa))
        U2 = math.atan((1 - ƒ) * math.tan(ϕb))

        # delta lambda (difference between longitude of a and longitude of b)
        Δλ = λb - λa

        λ = Δλ + 0

        while True:
            t = math.sqrt(
                (
                        math.cos(U2) * math.sin(λ)
                ) ** 2
            )
            t += (
                    (
                            math.cos(U1) * math.sin(U2) - math.sin(U1) * math.cos(U2) * math.cos(λ)
                    ) ** 2
            )
            sinσ = t ** 0.5
            cosσ = math.sin(U1) * math.sin(U2) - math.sin(U1) * math.cos(U2) * math.cos(λ)
            σ = math.atan2(sinσ, cosσ)

            sinα = math.cos(U1) * math.cos(U2) * math.sin(λ) / sinσ
            cos_sq_α = 1 - sinα ** 2
            cos2σm = cosσ - 2 * math.sin(U1) * math.sin(U2) / cos_sq_α
            C = ƒ * cos_sq_α * (4 + ƒ * (4 - 3 * cos_sq_α)) * 0.0625

            t = σ + C * sinσ * (cos2σm + C * cosσ * (-1 + 2 * cos2σm ** 2))
            L = Δλ + (1 - C) * ƒ * sinα * t

            if abs(L - λ) <= ε:
                break
            else:
                λ = L

        # performed once lambda is within the desired degree of accuracy
        u_sq = cos_sq_α * ((a ** 2 - b ** 2) / b ** 2)
        A = 1 + (u_sq * (4096 + u_sq * (-768 + u_sq * (320 - 175 * u_sq)))) / 16384
        B = u_sq * (256 + u_sq * (-128 + u_sq * (74 - 47 * u_sq))) / 1024

        t = cos2σm + 0.25 * B * (cosσ * (-1 + 2 * cos2σm ** 2))
        t -= (B * cos2σm / 6) * (-3 + 4 * math.sin(σ) ** 2) * (-3 + 4 * cos2σm ** 2)
        Δσ = B * sinσ * t
        s = b * A * (σ - Δσ)

        return s
