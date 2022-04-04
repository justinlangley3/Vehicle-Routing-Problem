# Standard Library
from copy import copy
from enum import Enum, auto

# Project Imports
from WGUPS.core.ruler import Ruler
from WGUPS.models.address import Address


class Method(Enum):
    ACO = auto()
    ConvexHull = auto()
    Genetic = auto()
    NearestNeighbor = auto()


class Solver:
    def __init__(self, use: Method, graph, packages, hub):
        self.algorithm = use
        self.graph = graph
        self.packages = copy(packages)
        self.hub = hub

    def solve(self):
        match self.algorithm:
            case Method.ACO:
                # not implemented, yet
                pass
            case Method.ConvexHull:
                hull = self._convex_hull()
                if hull is None:
                    path = [self.hub]
                    path.extend([package.address for package in self.packages])
                    path.append(self.hub)
                    return path
                return hull
            case Method.Genetic:
                # not implemented, yet
                pass
            case Method.NearestNeighbor:
                # not implemented, yet
                pass
            case _:
                raise ValueError

    def _convex_hull(self) -> list[Address] | None:
        def _remove_points(_in: list[Address], _from: list[Address]):
            for _point in copy(_from):
                if _point in _in:
                    _from.remove(_point)

        def _rotate_hull(_hull: list, _x: int):
            _size = len(_hull)
            _hull[:] = _hull[_x:_size] + _hull[0:_x]
            return _hull

        def _remove_duplicates(_from: list[Address]):
            seen = []
            for _address in copy(_from):
                if _address in seen:
                    _from.remove(_address)
                else:
                    seen.append(_address)

        def _jarvis(_points: list[Address]):
            _ruler = Ruler(calc_method=Ruler.Method.Haversine, unit=Ruler.unit.Miles)
            _leftmost = min(points, key=lambda x: x.coordinate.long)
            _index = points.index(_leftmost)
            _l = _index
            _hull = [_leftmost]
            while True:
                _q = (_l + 1) % len(points)
                for _i in range(len(points)):
                    if _i == _l:
                        continue
                    _d = Ruler.orientation(_points[_l].coordinate, _points[_i].coordinate, _points[_q].coordinate)
                    if _d == 2:
                        _q = _i
                _l = _q
                if _l == _index:
                    break
                _hull.append(_points[_q])
            return _hull

        # set up addresses to be path optimized
        points = [package.address for package in self.packages]
        points.insert(0, self.hub)
        _remove_duplicates(_from=points)

        if not len(points) > 3:
            return

        hull = _jarvis(_points=points)
        _remove_points(_in=hull, _from=points)

        # insert optimization for remaining points not present in the hull
        while len(points) > 0:
            best_ratio, best_point_index, insert_index = float('inf'), None, 0
            for i, point in enumerate(copy(points)):

                best_hull_cost, best_hull_index = float('inf'), 0
                for j, hull_point in enumerate(copy(hull)):
                    next_hull_point = hull[(j + 1) % len(hull)]

                    evaluated_cost = self.graph[hull_point][point] + self.graph[point][next_hull_point]
                    evaluated_cost -= self.graph[hull_point][next_hull_point]

                    if evaluated_cost < best_hull_cost:
                        best_hull_cost = evaluated_cost
                        best_hull_index = j

                next_point = hull[(best_hull_index + 1) % len(hull)]
                prev_cost = self.graph[hull[best_hull_index]][next_point]
                new_cost = self.graph[hull[best_hull_index]][point] + self.graph[point][next_point]
                ratio = new_cost / prev_cost

                if ratio < best_ratio:
                    best_ratio, best_point_index, insert_index = ratio, i, (best_hull_index + 1)

            next_point = points[best_point_index]
            points.remove(next_point)
            hull.insert(insert_index, next_point)

        # rotate until hub is at the start
        while hull[0] is not self.hub:
            _rotate_hull(hull, 1)
        # add hub to the end to close the path
        hull.append(self.hub)

        return hull

    @staticmethod
    def _meta_aco():
        # Set parameters, initialize pheromone trails
        # SCHEDULE_ACTIVITIES
        #   ConstructAntSolutions
        #   DaemonActions    {optional}
        #   UpdatePheromones
        # END_SCHEDULE_ACTIVITIES
        print("Not yet implemented")
        return

    @staticmethod
    def _meta_genetic():
        # Steps:
        # 1. Initialize population
        # 2. Fitness Function
        # 3. Selection
        # 4. Crossover
        # 5. Mutation
        print("Not yet implemented")
        return

    @staticmethod
    def _nearest_neighbor():
        # Steps:
        # 1. Initialize dataset
        # 3. For each visited point:
        #    - Graph search neighbors
        #    - Select nearest
        # 4. Assemble path
        print("Not yet implemented")
        return
