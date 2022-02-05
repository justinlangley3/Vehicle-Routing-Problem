# STL
import csv
import os
import pathlib
import pprint
import re
import sys
import timeit
import threading
import tkinter
from math import sqrt
from tkinter import ttk, filedialog

# Project packages
import wgups
import models
import structures

HUB = '4001 South 700 East'
address_graph: structures.Graph = structures.Graph(directed=False)
package_table: structures.HashTable = structures.HashTable()
printer = pprint.PrettyPrinter(indent=4, width=120)


# class MainWindow:
#     def __init__(self, master: tkinter.Tk):
#         return
#
#     def generate_action(self):
#         self.parse_package_data()
#         v, e = self.parse_distance_data()
#         generate_graph(v, e)
#         # delivery()
#
#     @staticmethod
#     def print_stats():
#         global package_table
#         global address_graph
#         mem_alloc_hash_table = sys.getsizeof(package_table)
#         mem_alloc_address_graph = sys.getsizeof(address_graph)
#
#         stats_to_print = f'----------\tData Structure Statistics\t----------\n' \
#                          f'Hash Table:\n' \
#                          f'\tMem Usage: {mem_usage_from_bytes(mem_alloc_hash_table)},\n' \
#                          f'{package_table.stats()}\n' \
#                          f'Address Graph:\n' \
#                          f'\tMem Usage: {mem_usage_from_bytes(mem_alloc_address_graph)}\n' \
#                          f'\t{str(address_graph)}'
#         print(stats_to_print)
#
# def generate_graph(v: list[str], e: list[list[str]]):
#     global address_graph
#
#     for i in range(len(v)):
#         address_graph.add_vertex(label=v[i])
#
#     vertices = list(address_graph.vertices.values())
#     for i in range(len(vertices)):
#         for j in range(len(e[i])):
#             if i == j:
#                 pass  # don't include an edge between a vertex and itself
#             else:
#                 # add an edge from each vertex to the other, allows forward/reverse lookup for additional mem usage
#                 address_graph.add_edge(
#                     source=address_graph.vertices[v[i]],
#                     dest=address_graph.vertices[v[j]],
#                     weight=float(e[i][j])
#                 )
#     address_graph.christofides()
#
#
# def get_shortest_path(start: structures.Graph.Vertex, current: structures.Graph.Vertex) -> tuple[float, str]:
#     global address_graph
#     path = ''
#     cost: float = 0
#     while current is not start and current is not None:
#         cost += current.cost
#         path = ' -> ' + current.label + path
#         current = current.pred
#         path = start.label + path
#     return cost, path
#
#
# def delivery() -> (str, list[int]):
#     global HUB
#     route = ''
#     package_ids: list[int] = []
#
#     source_package: Package.Package = package_table.get(1)
#     destination_package: Package.Package = package_table.get(31)
#     source = address_graph.vertices[source_package.street]
#     destination = address_graph.vertices[destination_package.street]
#
#     start = timeit.default_timer()
#     print('Running Dijkstra:')
#     address_graph.dijkstra(source)
#     cost, path = get_shortest_path(source, destination)
#     stop = timeit.default_timer()
#     print(f'exec={stop - start}, cost={cost}, path={path}')
#
#     start = timeit.default_timer()
#     print('Running A*:')
#     address_graph.a_star(source, destination)
#     cost, path = get_shortest_path(source, destination)
#     stop = timeit.default_timer()
#     print(f'exec={stop - start}, cost={cost}, path={path}')
#
#
# def mem_usage_from_bytes(s: int) -> str:
#     factor = 1024
#     count = 0
#     for i in range(1, 4):
#         if s / (i * factor) > 1:
#             count += 1
#     if count == 0:
#         return f'{s} B'
#     elif count == 1:
#         return f'{round(s / (count * factor))} KB'
#     elif count == 2:
#         return f'{round(s / (count * factor))} MB'
#     elif count == 3:
#         return f'{round(s / (count * factor))} GB'
#
#
# def build_adjacency_matrix(distances: dict):
#    global adjacency_matrix
#    vertices = list(distances.keys())
#    matrix = []
#    for i in range(len(vertices)):
#        edges = list(distances.get(vertices[i]))  # costs for building our adjacency matrix
#
#        row = []  # list for building our row
#        for j in range(len(edges)):  # values in cost list
#            if row.count([float(edges[j]), vertices[j]]) < 1:
#                row.append([float(edges[j]), vertices[j]])  # append street address, cost
#
#        if len(row) < len(vertices):  # check if we need to find costs to other nodes not contained in adjacency list
#            for j in range(len(distances)):
#                if len(distances.get(vertices[j])) < len(row):
#                    pass
#                elif row.count([float(distances.get(vertices[j])[i]), vertices[j]]) < 1:
#                    row.append([float(distances.get(vertices[j])[i]), vertices[j]])
#
#        row.sort()
#        matrix.append(row)
#    adjacency_matrix = dict(zip(distances.keys(), matrix))

def main():
    app = wgups.MainApp()
    app.mainloop()


if __name__ == '__main__':
    main()
