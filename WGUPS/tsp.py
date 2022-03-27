# Standard Library
import copy
from dataclasses import dataclass, field
from enum import Enum, auto

# Project Imports
from functools import reduce

import aco
import models
import adt
from ruler import Ruler


class Method(Enum):
    ACO = auto()
    ConvexHull = auto()
    Genetic = auto()
    NearestNeighbor = auto()


class TSPSolve:
    def __init__(self, use: Method, graph, truck):
        self.algorithm = use
        self.graph = graph
        self.nodes = truck.get_nodes()  # possibly something like this

    def solve(self):
        match self.algorithm:
            case Method.ACO:
                return self._meta_ACO()
            case Method.ConvexHull:
                return self._convex_hull()
            case Method.Genetic:
                return self._meta_genetic()
            case Method.NearestNeighbor:
                return self._nearest_neighbor()
            case _:
                raise ValueError

    def _convex_hull(self, g: structures.Graph, truck: models.Truck):
        ruler = Ruler(unit=Ruler.Units.Miles)

        def path_cost(p: list[models.Package]):
            return reduce(lambda a, b: a + b, map(ruler.compute_distance, [v.location for v in p]))

        def get_left_most(s, v):
            s = [i for i in v if i.location.long < s.location.long]
            return s

        vertices = truck.all_packages()
        try:
            print("TODO: Add graph size/degree method")
            assert None
        except AssertionError:
            print('There must be more than 3 vertices to run Convex-Hull')
            return

        sp = vertices[0]
        leftmost = get_left_most(sp, vertices)[0]
        path = [leftmost]

        while True:
            current = path[len(path) - 1]
            [selected_i, selected_p] = [0, None]

            for index, vertex in enumerate(vertices):
                if not selected_p or ruler.orientation(current.location, vertex.location, selected_p.location) == 2:
                    [selected_i, selected_p] = [index, vertex]

            del vertices[selected_i]

            if selected_p == leftmost:
                break

        best_index, free_index, free_vert = 0, 0, None
        while len(vertices) > 0:
            [best_ratio, best_vert_index, insert_index] = [float('inf'), None, 0]
            for free_index, free_vert in enumerate(vertices):
                [best_cost, best_index] = [float('inf'), 0]
                for [path_index, path_vert] in enumerate(path):
                    next_path_vert = path[(path_index + 1) % len(path)]
                    eval_cost = path_cost([path_vert, free_vert, next_path_vert])
                    eval_cost -= path_cost([path_vert, next_path_vert])

                    if eval_cost < best_cost:
                        [best_cost, best_index] = [eval_cost, path_index]

            next_vert = path[(best_index + 1) % len(path)]
            prev_cost = path_cost([path[best_index], next_vert])
            new_cost = path_cost([path[best_index], free_vert, next_vert])
            ratio = new_cost / prev_cost

            if ratio < best_ratio:
                [best_ratio, best_vert_index, insert_index] = [ratio, free_index, best_index + 1]
            [next_vert] = vertices[best_vert_index]
            path.insert(insert_index, next_vert)
            path.reverse()
            path.append(sp)
        return path

    def _meta_ACO(self):
        # Set parameters, initialize pheromone trails
        # SCHEDULE_ACTIVITIES
        #   ConstructAntSolutions
        #   DaemonActions    {optional}
        #   UpdatePheromones
        # END_SCHEDULE_ACTIVITIES
        print("Not yet implemented")
        return

    def _meta_genetic(self):
        # Steps:
        # 1. Initialize population
        # 2. Fitness Function
        # 3. Selection
        # 4. Crossover
        # 5. Mutation
        print("Not yet implemented")
        return

    def _nearest_neighbor(self):
        # Steps:
        # 1. Initialize dataset
        # 2. Choose value of K nearest data points (can be any integer)
        # 3. For each point:
        #    - Calculate cost to other points
        #    - Select for the lowest cost (Euclidean distance)
        # 4. Assemble path
        return
