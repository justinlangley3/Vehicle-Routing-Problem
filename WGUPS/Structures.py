from __future__ import annotations

import heapq, sys
import pprint
from dataclasses import dataclass, field
from enum import Enum, auto
from math import sqrt

import Debug
import inspect
import multiprocessing
from Debug import debug_msg
from typing import TypeVar, Generic
from functools import singledispatchmethod
from multiprocessing import Lock, Process, Semaphore, Barrier, Array, Queue

T = TypeVar('T')


@dataclass(eq=True, order=True, unsafe_hash=True)
class Node(Generic[T]):
    key: int = -1
    data: T = None
    next: Node = None
    prev: Node = None


class LinkedList(Generic[T]):
    # Class vars
    head: Node[T]
    tail: Node[T]
    size: int

    #
    # Magic Methods
    #
    def __init__(self) -> None:
        self.head = Node[None]
        self.tail = Node[None]
        self.size = 0

    def __len__(self) -> int:
        return self.size

    def __getitem__(self, i: int) -> Node[T]:
        assert self._is_element_index(i)
        count = 0
        if i < (self.size >> 1):
            for node in self:
                if count == i:
                    return node
                i += 1
        else:
            i = self.size - i
            for node in reversed(self):
                if count == i:
                    return node
                i += 1

    def __iter__(self) -> AscendingLinkedListIterator:
        return self.AscendingLinkedListIterator(self.head)

    def __reversed__(self) -> DescendingLinkedListIterator:
        return self.DescendingLinkedListIterator(self.tail)

    def __next__(self):
        pass

    def __repr__(self):
        r = ''
        count = 0
        for node in self:
            if node is None:
                return
            if count == 0:
                r += f'LinkedList(head={repr(node)})'
            else:
                r += ', '.join(f'node={repr(node)}')
            count += 1
        return r

    def __str__(self):
        return "\n->".join(str(node) for node in self)

    #
    # Public Methods
    #

    #
    # Get Operations
    def get_first(self) -> Node[T]:
        assert self.head is not None
        return self.head

    def get_last(self) -> Node[T]:
        assert self.tail is not None
        return self.tail

    #
    # Insert Operations
    def append(self, key: int, e: T) -> None:
        self._link_last(key, e)

    def prepend(self, key: int, e: T) -> None:
        self._link_first(key, e)

    @singledispatchmethod
    def add_all(self, c: list[list[int, T]]) -> bool:
        return self.add_all(self.size, c)

    @add_all.register
    def _(self, i: int, collection: list[list[int, T]]) -> bool:
        self._check_position_index(i)
        num_elements = len(collection)
        if num_elements == 0:
            return False
        predecessor, successor = Node[None]

        if i == self.size:
            predecessor = self.tail
        else:
            successor = self.node(i, False)
            predecessor = successor.prev

        for container in collection:
            new_node = Node(key=container[0], data=container[1], next=Node[None], prev=predecessor)
            # pointer adjustments
            if predecessor is None:
                self.head = new_node
            else:
                predecessor.next = successor
                successor.prev = predecessor
        self.size += num_elements

    #
    # Remove Operations
    def clear(self) -> None:
        for node in self:
            node.val = None
            node.next = None
            node.prev = None
        self.head = Node[None]
        self.tail = self.head
        self.size = 0

    def remove_first(self) -> T:
        h = self.head
        assert h is not None
        return self._unlink_first(h)

    def remove_last(self) -> T:
        t = self.tail
        assert t is not None
        return self._unlink_last(t)

    @singledispatchmethod
    def remove(self, e: T) -> bool:
        if e is None:
            for node in self:
                if node.data is None:
                    self._unlink(node)
                    return True
        else:
            for node in self:
                if node.data is e:
                    self._unlink(node)
                    return True
        return False

    @remove.register
    def _(self, i: int, is_key: bool) -> None:
        if is_key:
            for node in self:
                if node.key == i:
                    return self._unlink(node)
        else:
            self._check_element_index(i)
            return self._unlink(self.node(i, False))

    @remove.register
    def _(self, n: Node) -> None:
        for node in self:
            if n is node:
                return self._unlink(node)

    #
    # Size Operations
    def size(self) -> int:
        return self.size

    def is_empty(self) -> bool:
        return not self.head

    #
    # Conversion
    def to_list(self) -> list[tuple[int, T]]:
        return [(node.key, node.data) for node in self]

    #
    # Positional Operations
    @singledispatchmethod
    def node(self, i: int) -> Node[T]:
        assert self._is_element_index(i)
        count = 0
        if i < (self.size >> 1):
            for n in self:
                if count == i:
                    return n
                i += 1
        else:
            i = self.size - i
            for n in reversed(self):
                if count == i:
                    return n
                i += 1

    @node.register
    def _(self, i: int, is_key: bool) -> Node[T]:
        if is_key:
            for n in self:
                if n.key == i:
                    return n
            else:
                raise LookupError(debug_msg(Debug.Error.LOOKUP, inspect.currentframe()))
        return self.node(i)

    #
    # Search Operations
    def index_of(self, e: T) -> int:
        i = 0
        if e is None:
            for node in self:
                if node.data is None:
                    return i
                i += 1
        else:
            for node in self:
                if node is e:
                    return i
                i += 1

    def lastIndexOf(self, e: T) -> int:
        i = self.size
        if e is None:
            for node in reversed(self):
                i -= 1
                if node.val is None:
                    return i
        else:
            for node in reversed(self):
                i -= 1
                if node.val is e:
                    return i

    #
    # Private methods
    #

    #
    # Positional Operations
    def _is_element_index(self, i: int) -> bool:
        return 0 <= i <= self.size

    def _is_position_index(self, i: int) -> bool:
        return 0 <= i <= self.size

    def _check_element_index(self, i) -> None:
        if not self._is_position_index(i):
            raise IndexError(debug_msg(Debug.Error.INDEX, inspect.currentframe()))

    def _check_position_index(self, i) -> None:
        if not self._is_position_index(i):
            raise IndexError(debug_msg(Debug.Error.INDEX, inspect.currentframe()))

    #
    # Linking/Unlinking Operations
    def _link_first(self, key: int, e: T) -> None:
        head = self.head
        new_node = Node(key=key, data=e, next=head, prev=Node[None])
        self.head = new_node
        # pointer adjustments on old head
        if head is None:
            self.tail = new_node
        else:
            head.prev = new_node
        self.size += 1

    def _link_last(self, key: int, element: T) -> None:
        tail = self.tail
        new_node = Node(key=key, data=element, next=Node[None], prev=tail)
        self.tail = new_node
        # pointer adjustments on old tail
        if tail is None:
            self.head = new_node
        else:
            tail.next = new_node
        self.size += 1

    def _link_before(self, key: int, element: T, successor: Node[T]) -> None:
        predecessor = successor.prev
        new_node = Node(key=key, data=element, next=successor, prev=predecessor)
        successor.prev = new_node
        if predecessor is None:
            self.head = new_node
        else:
            predecessor.next = new_node
        self.size += 1

    def _unlink_first(self, head: Node[T]) -> T:
        e = head.data
        new_head = head.next
        del head.data, head.next
        self.head = new_head
        # pointer adjustments
        if new_head is None:
            self.tail = Node[None]
        else:
            new_head.prev = Node[None]
        self.size -= 1
        return e

    def _unlink_last(self, tail: Node[T]) -> T:
        e = tail.data
        new_tail = tail.prev
        del tail.data, tail.prev
        self.tail = new_tail
        # pointer adjustments
        if new_tail is None:
            self.head = Node[None]
        else:
            new_tail.next = Node[None]
        self.size -= 1
        return e

    def _unlink(self, n: Node[T]) -> T:
        assert n is not None
        if n is self.head:
            return self._unlink_first(n)
        if n is self.tail:
            return self._unlink_last(n)
        else:
            for node in self:
                if node.next is n:
                    e = node.next.data
                    next_node = n.next
                    prev_node = node
                    # adjust pointers
                    node.next = next_node
                    next_node.prev = prev_node
                    del n
                    self.size -= 1
                    return e
            else:
                raise LookupError(debug_msg(Debug.Error.LOOKUP, inspect.currentframe()))

    #
    # Member Classes
    #

    #
    # Iterators
    class AscendingLinkedListIterator:
        def __init__(self, head: Node[T]):
            self._node = head
            self._index = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self._node is Node[None]:
                raise StopIteration
            else:
                self._index += 1
                item = self._node
                self._node = self._node.next
                return item

    class DescendingLinkedListIterator:
        def __init__(self, tail: Node[T]):
            self._node = tail
            self._index = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self._node is Node[None]:
                raise StopIteration
            else:
                self._index += 1
                item = self._node
                self._node = self._node.prev
                return item


class HashTable(Generic[T]):
    # Class vars
    keys: int
    size: int
    table: list[LinkedList[T]]

    #
    # Magic Methods
    #
    def __init__(self, size: int = 4):
        self.VALUE_ERR = '\'Key cannot be a negative value\''
        self.keys = 0
        self.size = size
        self.table = [LinkedList[T]() for _ in range(size)]

    def __iter__(self):
        for bucket in self.table:
            yield bucket

    def __next__(self):
        pass

    def __repr__(self):
        return 'n'.join([f'{repr(self.table[i])}' for i in range(self.size)])

    def __str__(self):
        return '\n'.join(str(self.table[i]) for i in range(self.size))

    #
    # Public Methods
    #

    def is_empty(self) -> bool:
        return True if self.keys <= 0 else False

    #
    # Insertions
    def put(self, k: int, v: T) -> None:
        if k < 0:
            raise ValueError(debug_msg(Debug.Error.KEY_VALUE, inspect.currentframe()))

        # check if resize is required
        if self.keys >= (8 * self.size):
            self._resize(2 * self.size)

        b = self._hash(k)
        self.table[b].prepend(k, v)
        self.keys += 1

    #
    # Lookups
    def search(self, key: int) -> bool:
        # check if valid key
        if key < 0:
            raise ValueError(debug_msg(Debug.Error.VALUE, inspect.currentframe()))
        # find bucket
        b = self._hash(key)
        # perform search
        if self.table[b].node(key, True):
            return True
        # key wasn't found
        return False

    def get(self, key: int) -> T:
        # check if valid key
        if key < 0:
            raise ValueError(debug_msg(Debug.Error.KEY_VALUE, inspect.currentframe()))
        # find bucket
        b = self._hash(key)
        # retrieve data from the LinkedList
        return self.table[b].node(key, True).data

    #
    # Removes
    def remove(self, key: int) -> bool:
        # check if valid key
        if key < 0:
            raise ValueError(debug_msg(Debug.Error.KEY_VALUE, inspect.currentframe()))
        # remove the node containing the key
        b = self._hash(key)
        self.table[b].remove(key, True)
        self.keys -= 1

        # check if resize is needed
        if self.size > 4 and self.keys <= (2 * self.size):
            self._resize(int(0.5 * self.size))

        return True

    def clear(self) -> None:
        self.keys = 0
        for bucket in self.table:
            bucket.clear()
        self._resize(4)

    #
    # Statistics
    def stats(self) -> str:
        fill = '\n'
        if self.keys == 0:
            fill += f'\t\tbucket=1\t{{None}}\n'
            fill += f'\t\tbucket=2\t{{None}}\n'
            fill += f'\t\tbucket=3\t{{None}}\n'
            fill += f'\t\tbucket=4\t{{None}}\n'
        else:
            for i in range(self.size):
                if i == self.size:
                    fill += f'\t\tbucket={i}\t'
                    fill += '—'.join('[X]' for _ in range(len(self.table[i])))
                    fill += '\n'
                else:
                    fill += f'\t\tbucket={i}\t'
                    fill += '—'.join('[X]' for _ in range(len(self.table[i])))
                    fill += '\n'
        return (f'\t[----------\tHashTable Stats\t----------]'
                f'\n\t\tkeys={repr(self.keys)}'
                f'\n\t\tsize={repr(self.size)}'
                f'\n\t\tload={round(self.keys / self.size, 3)}'
                f'\n{fill}'
                f'\t[-------------------------------------]')

    #
    # Private Methods
    #

    #
    # Hashing
    def _hash(self, key: int) -> int:
        return key % self.size

    #
    # Resizing
    def _resize(self, new_table_size: int) -> None:
        old_table_size = len(self.table)
        self.size = new_table_size

        if self.is_empty():
            del self.table[new_table_size:]
            return

        # add new buckets, if table is growing
        if new_table_size > old_table_size:
            self.table.extend([LinkedList[T]() for _ in range(new_table_size - old_table_size)])

        # iterate previous buckets
        for i in range(old_table_size):
            # iterate LinkedList in current bucket
            for node in self.table[i]:
                if node is not Node[None]:
                    kv = (node.key, node.data)
                    b = self._hash(kv[0])
                    self.table[i].remove(node)
                    self.table[b].prepend(kv[0], kv[1])

        # remove empty buckets, if table is shrinking
        if new_table_size < old_table_size:
            del self.table[new_table_size:]


def _vertex_list_default_factory() -> list[Graph.Vertex]:
    return []


class Graph:
    class Vertex:
        label: str
        cost: float
        neighbors: list[Graph.Vertex]

        def __init__(self, label: str):
            self.label = label
            self.cost = float('inf')
            self.neighbors = _vertex_list_default_factory()
            self.pred = None
            self.children = list()
            self.degree = 0

        def __repr__(self):
            n = [n.label for n in self.neighbors]
            return f'label={self.label}, degree={self.degree}, cost={self.cost}'

        def __hash__(self):
            return hash(self.label)

        def __lt__(self, other):
            return self.cost < other.cost

    #    class Edge:
    #        source: Graph.Vertex
    #        destination: Graph.Vertex
    #        weight: float
    #
    #        def __init__(self, id: int, source: Graph.Vertex, dest: Graph.Vertex, weight: float = 1.0):
    #            self.id = id
    #            self.source = source
    #            self.destination = dest
    #            self.weight = weight
    #
    #        def __hash__(self):
    #            return hash(self.id)
    #
    #        def __lt__(self, other):
    #            return self.weight < other.weight
    #
    #        def __gt__(self, other):
    #            return self.weight < other.weight
    #
    #        def __le__(self, other):
    #            return self.weight <= other.weight
    #
    #        def __ge__(self, other):
    #            return self.weight >= other.weight
    #
    #        def __eq__(self, other):
    #            return self is other.weight
    #
    #        def __ne__(self, other):
    #            return self.weight is not other.weight

    directed: bool
    vertices: dict[str, Graph.Vertex]
    edges: dict[[Graph.Vertex, Graph.Vertex], float]
    edge_count: int

    def __init__(self, directed=False):
        self.edges = dict()
        self.vertices = dict()
        self.directed = directed
        self.edge_count = 0

    def add_vertex(self, label: str) -> Vertex:
        if self.vertices.get(label):
            return self.vertices[label]
        else:
            v = self.Vertex(label=label)
            self.vertices[label] = v
            return v

    def remove_vertex(self, label: str) -> Vertex:
        current = self.vertices[label]
        if current:
            for k, v in self.vertices.items():
                # the vertex selected for removal is removed from all adjacency lists
                v.neighbors.remove(current)
        return self.vertices.pop(label)

    def add_edge(self, source: Vertex, dest: Vertex, weight: float) -> tuple:
        neighbors = source.neighbors
        neighbors.append(dest)
        self.edges[(source, dest)] = weight

        if not self.directed:
            neighbors = dest.neighbors
            neighbors.append(source)
            self.edges[(dest, source)] = weight

        return source, dest, weight

    def remove_edge(self, source: Vertex, dest: Vertex) -> tuple:
        weight = float('inf')
        if source and dest:
            source.neighbors.remove(dest)
            # if a weight other than 'inf' was assigned it will get returned
            weight = self.edges.pop([(source, dest)])
        if source and dest and not self.directed:
            dest.neighbors.remove(source)
            self.edges.pop([(dest, source)])
        return source, dest, weight

    def get_MST(self):
        return self._prim_mst()

    # TODO: Check correctness of this implementation
    def _prim_mst(self):
        mst = []
        mst_cost = 0.0

        seen = set()

        # create a priority queue, containing all vertices, with cost initialized to 'inf'
        queue: list[tuple[float, Graph.Vertex]] = [
            (
                v.cost,  # cost
                v  # vertex
            )
            for k, v in self.vertices.items()
        ]
        # select an arbitrary index and set its weight to 0.0
        heapq.heapreplace(queue, (0.0, queue[0][1]))

        while queue:
            cost, u = heapq.heappop(queue)
            seen.add(u)

            min_weight: float = float('inf')
            min_vertex: Graph.Vertex
            for n in u.neighbors:
                if n in seen:
                    continue
                else:
                    if (self.edges[(u, n)], n) > queue[0]:
                        heapq.heapreplace(queue, (self.edges[(u, n)], n))
                    if self.edges[(u, n)] < min_weight:
                        min_weight = self.edges[(u, n)]
                        min_vertex = n
                        min_vertex.pred = u
                        min_vertex.cost = min_weight
                        u.cost = min_weight

            mst.append((u, min_vertex))
            mst_cost += min_vertex.cost
            u.degree += 1
            min_vertex.degree += 1
        return mst, mst_cost

    @staticmethod
    def _get_odd_vertices(mst):
        odd = list()
        for edge in mst:
            for vertex in edge:
                if (vertex.degree % 2 != 0) and (vertex.degree != 0) and vertex not in odd:
                    odd.append(vertex)
        return odd

    def _minimum_matching(self, mst, odd_vertices: list):
        import random
        random.shuffle(odd_vertices)

        while odd_vertices:
            v = odd_vertices.pop()
            min_cost = float('inf')
            min_v = None

            for u in odd_vertices:
                if v != u and self.edges[(v, u)] < min_cost:
                    min_cost = self.edges[(v, u)]
                    min_v = u
            mst.append((v, min_v, min_cost))
            odd_vertices.remove(min_v)

    def _find_eulerian_tour(self, matched_mst):
        neighbors = {}
        for edge in matched_mst:
            if edge[0] not in neighbors:
                neighbors[edge[0]] = []

            if edge[1] not in neighbors:
                neighbors[edge[1]] = []

            neighbors[edge[0]].append(edge[1])
            neighbors[edge[1]].append(edge[0])

        start_vertex = matched_mst[0][0]
        eulerian_circuit = [neighbors[start_vertex][0]]

        while len(matched_mst) > 0:
            for i, v in enumerate(eulerian_circuit):
                if len(neighbors[v]) > 0:
                    break
            while len(neighbors[v]) > 0:
                w = neighbors[v][0]
                self._remove_edge_from_matched_mst(matched_mst, v, w)
                del neighbors[v][(neighbors[v].index(w))]
                del neighbors[w][(neighbors[w].index(v))]
                i += 1
                eulerian_circuit.insert(i, w)
                v = w
        return eulerian_circuit

    @staticmethod
    def _remove_edge_from_matched_mst(matched_mst, u, v):
        for i, item in enumerate(matched_mst):
            if (item[0] == v and item[1] == u) or (item[0] == u and item[1] == v):
                del matched_mst[i]
        return matched_mst

    def christofides(self):
        tree = self._prim_mst()[0]
        odd_vertices = self._get_odd_vertices(tree)
        self._minimum_matching(tree, odd_vertices)
        euler = self._find_eulerian_tour(tree)

        current = euler[0]
        path = [current]
        visited = {v: False for v in euler}
        length = 0

        for v in euler[1:]:
            if not visited[v]:
                path.append(v)
                visited[v] = True
                length += self.edges[(current, v)]
                current = v
        path.append(path[0])

        printer = pprint.PrettyPrinter(indent=4, width=120)
        printer.pprint(path)

    def a_star(self, source: Vertex, dest: Vertex):
        def get_edge_weight(s: Graph.Vertex, d: Graph.Vertex):
            return self.edges[(s, d)]

        path = {v: None for k, v in self.vertices.items()}
        f_cost = {v: v.cost for k, v in self.vertices.items()}
        g_cost = {v: v.cost for k, v in self.vertices.items()}

        path[source] = 0.0
        f_cost[source] = 0.0
        g_cost[source] = 0.0

        queue = [(0.0, source)]

        while queue:
            current_f_cost, current = heapq.heappop(queue)
            if current is dest:
                return f_cost, path
            for n in current.neighbors:
                if n is dest:
                    continue
                else:
                    temp_g_cost = g_cost[current] + self.edges[(current, n)]
                    if temp_g_cost < g_cost[n]:
                        n.pred = current
                        g_cost[n] = temp_g_cost
                        heuristic = get_edge_weight(n, dest)
                        f_cost[n] = temp_g_cost + heuristic
                        n.cost = temp_g_cost + heuristic
                        path[n] = current
                        heapq.heappush(queue, (f_cost[n], n))
        return f_cost, path

    def dijkstra(self, source: Vertex):
        costs = {v: v.cost for k, v in self.vertices.items()}
        path = {v: None for k, v in self.vertices.items()}

        costs[source] = 0.0
        queue = [(0.0, source)]

        while queue:
            current_cost, current = heapq.heappop(queue)

            n: Graph.Vertex
            for n in current.neighbors:
                weight = current_cost + self.edges[(current, n)]

                if weight < costs[n]:
                    n.pred = current
                    n.cost = weight
                    costs[n] = weight
                    path[n] = current
                    heapq.heappush(queue, (weight, n))
        return costs, path
