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

import Package
import Structures

HUB = '4001 South 700 East'
address_graph: Structures.Graph = Structures.Graph(directed=False)
package_table: Structures.HashTable = Structures.HashTable()
printer = pprint.PrettyPrinter(indent=4, width=120)


class MainWindow:
    def __init__(self, master: tkinter.Tk):
        files = check_for_data_sources()
        lbl_package = tkinter.ttk.Label(master, text='Confirm packages.csv:')
        lbl_package.grid(column=0, row=0, sticky=tkinter.W, padx=5, pady=5)

        self.text_package = tkinter.StringVar()
        self.text_package.set(files[0])
        entry_package = tkinter.ttk.Entry(master, textvariable=self.text_package, width=40)
        entry_package.grid(column=0, row=1, padx=5, pady=5)

        btn_package = tkinter.ttk.Button(master, text='...', width=4,
                                         command=lambda: self.file_selection_diag(self.text_package))
        btn_package.grid(column=1, row=1, padx=0, pady=5)

        lbl_distance = tkinter.ttk.Label(master, text='Confirm distances.csv:')
        lbl_distance.grid(column=0, row=2, sticky=tkinter.W, padx=5, pady=5)

        self.text_distance = tkinter.StringVar()
        self.text_distance.set(files[1])
        entry_distance = tkinter.ttk.Entry(master, textvariable=self.text_distance, width=40)
        entry_distance.grid(column=0, row=3, padx=5, pady=5)

        btn_distance = tkinter.ttk.Button(master, text='...', width=4,
                                          command=lambda: self.file_selection_diag(self.text_distance))
        btn_distance.grid(column=1, row=3, padx=0, pady=5)

        btn_generate = tkinter.ttk.Button(master, text='Generate Package Load Plan',
                                          command=lambda: self.generate_action())
        btn_generate.grid(column=0, columnspan=2, row=4, pady=10)
        self.generate_action()

    @staticmethod
    def file_selection_diag(text: tkinter.StringVar):
        path = tkinter.filedialog.askopenfilename()
        text.set(path)
        return path

    def generate_action(self):
        self.parse_package_data()
        v, e = self.parse_distance_data()
        generate_graph(v, e)
        # delivery()

    @staticmethod
    def print_stats():
        global package_table
        global address_graph
        mem_alloc_hash_table = sys.getsizeof(package_table)
        mem_alloc_address_graph = sys.getsizeof(address_graph)

        stats_to_print = f'----------\tData Structure Statistics\t----------\n' \
                         f'Hash Table:\n' \
                         f'\tMem Usage: {mem_usage_from_bytes(mem_alloc_hash_table)},\n' \
                         f'{package_table.stats()}\n' \
                         f'Address Graph:\n' \
                         f'\tMem Usage: {mem_usage_from_bytes(mem_alloc_address_graph)}\n' \
                         f'\t{str(address_graph)}'
        print(stats_to_print)

    def parse_package_data(self):
        path = self.text_package.get()
        csv_data = self.parse_csv(path)[1:]
        for row in csv_data:
            package_table.put(int(row[0]), Package.Package(row))
        # print(package_table)
        # print(package_table.stats())

    def parse_distance_data(self) -> (list, list):
        path = self.text_distance.get()
        lines = self.parse_csv(path)

        # vertices are the addresses contained in the csv header
        v = [i.split(",\n")[1] for i in lines[0][1:]]

        # edges are represented by the weights contained in the rows, cols following the csv header
        # we also only take rows 1 onward, because row 0 is the csv header containing our vertices
        # the lambda function selects non-null entries, for which the filter adds to our list
        # this simply removes null comma separated values e.g. (,,,)
        e = [list(filter(lambda x: x != "", line[1:])) for line in lines[1:]]
        return v, e

    @staticmethod
    def parse_csv(path):
        with open(path, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile, dialect='excel')
            return list(reader)


class ResultsWindow:
    def __init__(self, master: tkinter.Tk):
        return


def generate_graph(v: list[str], e: list[list[str]]):
    global address_graph

    for i in range(len(v)):
        address_graph.add_vertex(label=v[i])

    vertices = list(address_graph.vertices.values())
    for i in range(len(vertices)):
        for j in range(len(e[i])):
            if i == j:
                pass  # don't include an edge between a vertex and itself
            else:
                # add an edge from each vertex to the other, allows forward/reverse lookup for additional mem usage
                address_graph.add_edge(
                    source=address_graph.vertices[v[i]],
                    dest=address_graph.vertices[v[j]],
                    weight=float(e[i][j])
                )
    address_graph.christofides()


def get_shortest_path(start: Structures.Graph.Vertex, current: Structures.Graph.Vertex) -> tuple[float, str]:
    global address_graph
    path = ''
    cost: float = 0
    while current is not start and current is not None:
        cost += current.cost
        path = ' -> ' + current.label + path
        current = current.pred
        path = start.label + path
    return cost, path


def delivery() -> (str, list[int]):
    global HUB
    route = ''
    package_ids: list[int] = []

    source_package: Package.Package = package_table.get(1)
    destination_package: Package.Package = package_table.get(31)
    source = address_graph.vertices[source_package.street]
    destination = address_graph.vertices[destination_package.street]

    start = timeit.default_timer()
    print('Running Dijkstra:')
    address_graph.dijkstra(source)
    cost, path = get_shortest_path(source, destination)
    stop = timeit.default_timer()
    print(f'exec={stop - start}, cost={cost}, path={path}')

    start = timeit.default_timer()
    print('Running A*:')
    address_graph.a_star(source, destination)
    cost, path = get_shortest_path(source, destination)
    stop = timeit.default_timer()
    print(f'exec={stop - start}, cost={cost}, path={path}')


def mem_usage_from_bytes(s: int) -> str:
    factor = 1024
    count = 0
    for i in range(1, 4):
        if s / (i * factor) > 1:
            count += 1
    if count == 0:
        return f'{s} B'
    elif count == 1:
        return f'{round(s / (count * factor))} KB'
    elif count == 2:
        return f'{round(s / (count * factor))} MB'
    elif count == 3:
        return f'{round(s / (count * factor))} GB'


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


def check_for_data_sources():
    package_file = ''
    distance_file = ''
    default_dir_ = pathlib.Path('./data/')

    package_re = re.compile(r"package([0-9A-Za-z{[(\\/\])}\-!@#$%^&_+=,.'`~])*(.csv)")
    distance_re = re.compile(r"distance([0-9A-Za-z{[(\\/\])}\-!@#$%^&_+=,.'`~])*(.csv)")

    for entry in os.listdir(default_dir_):
        if entry is None:
            return
        full_path = default_dir_.absolute().joinpath(entry)
        if package_re.match(entry) and package_file is not None:
            package_file = full_path.as_posix()
        if distance_re.match(entry) and distance_file is not None:
            distance_file = full_path.as_posix()
    return package_file, distance_file


def main():
    check_for_data_sources()
    root = tkinter.Tk()
    form_h = '380'  # form width
    form_v = '180'  # form height
    # math for placing the form horizontally and vertically centered
    center_h = str(int(root.winfo_screenwidth() / 2) - int(int(form_h) / 2))
    center_v = str(int(root.winfo_screenheight() / 2) - int(int(form_v) / 2))
    # configure form size
    root.geometry(form_h + 'x' + form_v + '+' + center_h + '+' + center_v)
    root.title('WGUPS')
    # root.resizable(False, False)
    root.tk.call('tk', 'scaling', 1.2)
    app = MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()
