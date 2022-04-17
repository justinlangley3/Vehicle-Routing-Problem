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
        """
        Big-O Analysis:
            O(n^2):
              Jarvis march is O(nlogh), to find the hull. It's output sensitive to h, the number of points on the hull.
              The remainder is an insertion sort, with a cost heuristic to form the full boundary.
              Insertion sort runs in O(n^2), giving use the time complexity annotated above

        Returns: list[Address] | None

        """
        def _remove_points(_in: list[Address], _from: list[Address]):
            """Removes hull points from the path"""
            for _point in copy(_from):
                if _point in _in:
                    _from.remove(_point)

        def _rotate_hull(_hull: list, _x: int):
            """Used to rotate the hub location to the start of the lix"""
            _size = len(_hull)
            _hull[:] = _hull[_x:_size] + _hull[0:_x]
            return _hull

        def _remove_duplicates(_from: list[Address]):
            """Remove duplicate points, for some reason I had an issue with duplicate points"""
            seen = []
            for _address in copy(_from):
                if _address in seen:
                    _from.remove(_address)
                else:
                    seen.append(_address)

        def _jarvis(_points: list[Address]) -> list[Address]:
            """
            Big-O Analysis:
                O(n•h), n is the number of vertices, h is the number of points that form the hull
                        if h is shown to be logn, then it performs better than the alternative
                        Graham's scan algorithm
            Args:
                _points: list[Address]

            Returns: list[Address]

            """
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

        # Big-0: O(n^2), this is just insertion sort with a cost evaluation heuristic
        #                graph search is an amortized constant time operation, so we can discount the rest
        #                as sequential constant time operations

        # insert optimization for remaining points not present in the hull
        while len(points) > 0:
            best_ratio, best_point_index, insert_index = float('inf'), None, 0

            # on each remaining point
            for i, point in enumerate(copy(points)):

                best_hull_cost, best_hull_index = float('inf'), 0
                for j, hull_point in enumerate(copy(hull)):
                    # for each point in the hull

                    # retrieve the next hull point beyond our current position
                    next_hull_point = hull[(j + 1) % len(hull)]

                    # evaluate its cost
                    evaluated_cost = self.graph[hull_point][point] + self.graph[point][next_hull_point]
                    evaluated_cost -= self.graph[hull_point][next_hull_point]

                    # if its cost is better than the best so far, then update best hull cost
                    if evaluated_cost < best_hull_cost:
                        best_hull_cost = evaluated_cost
                        best_hull_index = j

                # retrieve the next point from our points not on the hull
                next_point = hull[(best_hull_index + 1) % len(hull)]

                # find the previous_cost, the new_cost, and the ratio
                prev_cost = self.graph[hull[best_hull_index]][next_point]
                new_cost = self.graph[hull[best_hull_index]][point] + self.graph[point][next_point]
                ratio = new_cost / prev_cost

                # if the ratio is better than the best so far
                if ratio < best_ratio:
                    # update it to the best ratio,
                    # and update our best found index, as well as insertion index
                    best_ratio, best_point_index, insert_index = ratio, i, (best_hull_index + 1)

            # set the next point to the best index found so far
            next_point = points[best_point_index]

            # remove it from the list of remaining points and insert it into the hull
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
