import Package
import Structures
import csv
import datetime
import os
import pathlib
import re
import tkinter as tk
from tkinter import filedialog, ttk


class MainWindow:
    def __init__(self, master: tk.Tk):
        files = check_for_data_sources()
        lbl_package = ttk.Label(master, text='Confirm packages.csv:')
        lbl_package.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

        text_package = tk.StringVar()
        text_package.set(files[0])
        entry_package = ttk.Entry(master, textvariable=text_package, width=40)
        entry_package.grid(column=0, row=1, padx=5, pady=5)

        btn_package = ttk.Button(master, text='...', width=4,
                                 command=lambda: self.file_selection_diag(text_package))
        btn_package.grid(column=1, row=1, padx=0, pady=5)

        lbl_distance = ttk.Label(master, text='Confirm distances.csv:')
        lbl_distance.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)

        text_distance = tk.StringVar()
        text_distance.set(files[1])
        entry_distance = ttk.Entry(master, textvariable=text_distance, width=40)
        entry_distance.grid(column=0, row=3, padx=5, pady=5)

        btn_distance = ttk.Button(master, text='...', width=4,
                                  command=lambda: self.file_selection_diag(text_distance))
        btn_distance.grid(column=1, row=3, padx=0, pady=5)

        btn_generate = ttk.Button(master, text='Generate Package Load Plan',
                                  command=lambda: self.load_package_data(text_package.get()))
        btn_generate.grid(column=0, columnspan=2, row=4, pady=10)

    @staticmethod
    def file_selection_diag(text: tk.StringVar):
        path = filedialog.askopenfilename()
        text.set(path)
        return path

    def generate_action(self):
        return

    @staticmethod
    def load_package_data(path):
        pkg = Package.Package(1, "42 Wallaby Way", "Sydney", "AU", "2000", "EOD", 40, "Some notes")
        pkg_table = Structures.HashTable()
        with open(path, "r") as f:
            for line in f:
                # we don't care about lines that don't contain a package ID
                if re.match("[0-9]+", line[0]):
                    # our file was converted from .xlsx to .csv in Excel
                    # seems to have added ",,,,,,\n" to the end of each line in the .csv
                    d = line.strip(",,,,,,\n")
                    d = d.split(",")
                    pkg = Package.Package(d[0], d[1], d[2], d[3], d[4], d[5], d[6], ''.join(d[7:]) or '')
                    pkg_table.insert(pkg.id_val, pkg)
        f.close()
        print(pkg_table.stats())
        return pkg_table

    def load_distance_data(self, path):
        self.parse_csv(path)
        return

    @staticmethod
    def parse_csv(path):
        with open(path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f, dialect='excel')
            data = list(reader)[8:]
        print(data)


class ResultsWindow:
    def __init__(self, master: tk.Tk):
        return


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
    root = tk.Tk()
    print()
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