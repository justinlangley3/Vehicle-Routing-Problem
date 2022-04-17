from __future__ import annotations

# STL Imports
from typing import Generic, TypeVar

# Project Imports
from .hashtable import HashTable

T = TypeVar('T')


class Graph(Generic[T]):
    _edges: HashTable[T, HashTable[T, float]] = HashTable()  # Store Graph edges using our HashTable class

    def __getitem__(self, item):
        return self._edges[item]

    def __len__(self):
        return len(self._edges)

    def __iter__(self):
        for edge in self._edges:
            yield edge

    def __next__(self):
        pass

    def __repr__(self):
        return 'Graph('.join([''.join(f'{i}: {edge})\n') for i, edge in enumerate(self._edges)]) + ')'

    def add_vertex(self, vert: T) -> None:
        """
        Adds a vertex to the graph
        Each vertex maintains its own adjacency list as a subsequent HashTable
        """
        if not self._edges[vert]:
            self._edges[vert] = HashTable[T, float]()

    def add_edge(self, vert_a: T, vert_b: T, dist: float, is_directed: bool = False) -> None:
        """
        Adds a directed or undirected edge accordingly
        """

        def _add_single_edge(a, b, d):
            # don't add a vertex as its own neighbor,
            # the distance to itself is simply 0.0
            if a == b:
                return
            if not self._edges[a][b]:
                self._edges[a][b] = d

        if is_directed:
            # add as a directed edge
            _add_single_edge(vert_a, vert_b, dist)
        else:
            # add the edge in both directions
            _add_single_edge(vert_a, vert_b, dist)
            _add_single_edge(vert_b, vert_a, dist)

    def remove_vertex(self, v: T) -> None:
        """
        Removes a vertex
          1) Removes itself from any neighbor containing it
          2) Deletes the vertex
        """
        # get neighbors
        neighbors = self._edges[v]

        # remove the vertex from the adjacency list of all neighbors
        for neighbor in neighbors:
            neighbor_v: HashTable = self._edges[neighbor]
            del neighbor_v[v]

        # remove the vertex
        del self._edges[v]

    def remove_edge(self, vert_a: T, vert_b: T, is_directed: bool = False) -> None:
        """
        Removes a directed or undirected edge accordingly
        """

        def _remove_single_edge(a, b):
            neighbors: HashTable = self._edges[a]
            if neighbors.search(b):
                del neighbors[b]

        if is_directed:
            # remove the directed edge
            _remove_single_edge(vert_a, vert_b)
        else:
            # remove the edge in both directions
            _remove_single_edge(vert_a, vert_b)
            _remove_single_edge(vert_b, vert_a)

    def distance_of(self, vert_a: T, vert_b: T) -> float:
        print(f'a: {vert_a}\nb: {vert_b}')
        print(self._edges[vert_a][vert_b])
        return self._edges[vert_a][vert_b]

    def degree(self, vert_a: T) -> int:
        """
        Finds the degree of a vertex
        Args:
            vert_a: T

        Returns: int

        """
        return len(self._edges[vert_a])

    def vertex_sum(self) -> int:
        return len(self._edges)

    def edge_sum(self) -> int:
        """
        Finds the number of edges in the graph.
        Assumes the graph is undirected at the moment.

        Returns: int

        """
        d = 0
        for vertex in self._edges:
            d += len(vertex)
        return d // 2
