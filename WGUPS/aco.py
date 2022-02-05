
from random import randint, choice
from threading import Thread


class AntGraph(object):
    def __init__(self, weights: list, rank: int):
        self.weights = weights
        self.rank = rank


class ACO(object):
    def __init__(self,
                 generations: int = 80,
                 ant_count: int = 50,
                 alpha: float = 1.0,
                 beta: float = 0.8,
                 rho: float = 0.5,
                 q: int = 500):
        self.Q = q  # Pheromone constant
        self.rho = rho  # Decay rate
        self.beta = beta  # Distance weight
        self.alpha = alpha  # Pheromone weight
        self.ant_count = ant_count  # Threads
        self.generations = generations  # Iterations


class _Ant(object):
    def __init__(self, graph=None, colony=None):
        self.colony = colony
        self.graph = graph




