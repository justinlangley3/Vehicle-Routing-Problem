# STL
import csv
import glob
import os
import pathlib
import re
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

# Project packages
from WGUPS import structures, models


# Application State Control
#

class Control:
    """
    A simple class for application control
    """

    def __init__(self):
        return


# GUI Entry Point
#
class MainApp(tk.Tk):
    def __init__(self, frame_stack=None, master=None):
        super().__init__()
        # variables for frame management
        self.frame_count = -1
        self.frames = {}

        self.title('WGUPS')
        self.tk.call('tk', 'scaling', 1.2)

        self.setup_view = SetupView(master=self)
        self.setup_view.pack()
        self.push_frame(frame=self.setup_view)
        return

    def push_frame(self, frame):
        self.frame_count += 1
        self.frames[self.frame_count] = frame
        self.frames[self.frame_count].lift()
        self._resize(frame)
        return

    def pop_frame(self):
        self.frames[self.frame_count].destroy()
        self.frame_count -= 1
        self.frames[self.frame_count].lift()
        self._resize(self.frames[self.frame_count])
        return

    def _resize(self, frame):
        # screen dimensions
        screen_w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()

        # frame dimensions
        frame_w, frame_h = frame.size

        # math to locate x,y coords required to center the window upon resize
        center_w = str((screen_w // 2) - (frame_w // 2))
        center_h = str((screen_h // 2) - (frame_h // 2))

        self.geometry(str(frame_w) + 'x' + str(frame_h) + '+' + str(center_w) + '+' + str(center_h))

        return


# Application Views
#
class DeliveryView(ttk.Frame):
    def __init__(self, master=None):
        super().__init__()

        return


class LoadConfirmationView(ttk.Frame):
    def __init__(self, master=None):
        super().__init__()

        return


class SetupView(ttk.Labelframe):
    def __init__(self, master=None):
        super().__init__(text='Data Sources')
        # define the frame size, so resizing can work automatically
        self.size = (300, 190)

        # get data files
        files = fetch_data_sources()

        # setup StringVar objects for holding path text
        self.text_distance = tk.StringVar()
        self.text_package = tk.StringVar()
        self.text_distance.set(str(files[1]))
        self.text_package.set(str(files[0]))

        # setup label widgets
        self.label_distance_tooltip = ttk.Label(
            master=self,
            text='Confirm distances.csv'
        )
        self.label_package_tooltip = ttk.Label(
            master=self,
            text="Confirm packages.csv:"
        )
        self.label_distance_tooltip.grid(
            column=0,
            row=2,
            sticky=tk.W,
            padx=5,
            pady=5
        )
        self.label_package_tooltip.grid(
            column=0,
            row=0,
            sticky=tk.W,
            padx=5,
            pady=5
        )

        # setup entry widgets
        self.entry_distance_path = ttk.Entry(
            master=self,
            textvariable=self.text_distance,
            width=40
        )
        self.entry_package_path = ttk.Entry(
            master=self,
            textvariable=self.text_package,
            width=40
        )
        self.entry_distance_path.grid(
            column=0,
            row=3,
            padx=5,
            pady=5
        )
        self.entry_package_path.grid(
            column=0,
            row=1,
            sticky=tk.W,
            padx=5,
            pady=5
        )

        # setup button widgets
        self.button_configure = ttk.Button(
            master=self,
            text='Configure Trucks',
            command=None  # TODO: write logic to handle changing screens and maintain state
        )
        self.button_distance = ttk.Button(
            master=self,
            text='...',
            width=4,
            command=lambda: file_selection_diag(self.text_distance)
        )
        self.button_package = ttk.Button(
            master=self,
            text='...',
            width=4,
            command=lambda: file_selection_diag(self.text_package)
        )
        self.button_configure.grid(
            column=0,
            columnspan=2,
            row=4,
            pady=10
        )
        self.button_distance.grid(
            column=1,
            row=3,
            padx=0,
            pady=5
        )
        self.button_package.grid(
            column=1,
            row=1,
            padx=0,
            pady=5
        )


class PackageTreeview(ttk.Treeview):
    def __init__(self, master=None):
        super().__init__()

        self.columns = ["ID", "Street", "City", "State", "Zip", "Mass (kg)", "Deadline", "Notes"]

        num_columns = len(self.columns)
        for i in range(num_columns):
            self.heading(column=i, option=self.columns[i])

    def on_double_click(self, event):
        rowid = self.identify_row(event.y)
        column = self.identify_column(event.x)

        pady = 0
        x, y, width, height = self.bbox(rowid, column)

        text = self.item(rowid, 'text')
        self.entry_popup = EntryPopup(self, rowid, text)
        self.entry_popup.place(x=0, y=y + pady, anchor=tk.W, relwidth=1)


class EntryPopup(ttk.Entry):
    def __init__(self, master, iid, text, **kw):
        super().__init__(master, **kw)
        self.tv = master
        self.iid = iid

        self.insert(0, text)
        self['exportselection'] = False
        self.focus_force()
        self.bind("<Return>", self.on_return)
        self.bind("<Control-a>", self.select_all)
        self.bind("<Escape>", lambda *ignore: self.destroy())

    def on_return(self, event):
        self.tv.item(self.iid, text=self.get())
        self.destroy()

    def select_all(self, *ignore):
        self.selection_range(0, 'end')
        return 'break'


class TruckView(ttk.Frame):
    def __init__(self, master=None):
        super().__init__()
        self.tabs = {}
        self.num_trucks = 2

        self.tab_control = ttk.Notebook(master)

        # setup tabs for different trucks
        self.tabs[0] = PackageTreeview(self.tab_control)
        self.tabs[1] = PackageTreeview(self.tab_control)

        # add info text to the tab
        self.tab_control.add(self.tabs[0], text='Truck1')
        self.tab_control.add(self.tabs[1], text='Truck2')

        return

    def add_truck(self):
        self.num_trucks += 1
        self.tabs[self.num_trucks] = PackageTreeview(self.tab_control)
        self.tab_control.add(self.tabs[self.num_trucks], text=f'Truck{self.num_trucks}')

        return

    def del_truck(self):
        self.tab_control.hide(tab_id=self.num_trucks)

        self.num_trucks -= 1
        return

    def add_package(self):
        return

    def remove_package(self):
        return


# Helpers
#
def file_selection_diag(text: tk.StringVar = None) -> str:
    """
    Function to create a file selection dialog
    :param text: an optional tk.StringVar, if provided, will have its text element set as the path returned
    :return: str
    """
    path = filedialog.askopenfilename()
    text.set(path)
    return path


def fetch_data_sources():
    """
    Function to locate the paths of the most recent package and distance data files<br>
    Assumes these files are in .csv format, and located in './data' relative to the application directory
    :return: tuple[Path, Path]
    """
    # Note: 2022-03-01 would appear after 2022-01-01 in ascending order
    #       We can use the sorted() function to alter the order of the files returned by glob()
    #       By specifying 'key=os.path.getctime', we can sort by the file(s) creation time
    #       If we specify 'reverse=True' the most recent items will be at the front of the list
    #       Conversely, if we don't specify 'reverse=True', then we could use pop() to get the most recent

    # a list of .csv files containing 'package' in the file name, sorted by creation time
    package_files = sorted(glob.glob('./data/*package*.csv'), key=os.path.getctime, reverse=True)

    # a list of .csv files containing 'distance' in the file name, sorted by creation time
    distance_files = sorted(glob.glob('./data/*distance*.csv'), key=os.path.getctime, reverse=True)

    # resolve the most recent from each to an absolute path
    package_file = pathlib.Path(package_files[0]).resolve()
    distance_file = pathlib.Path(distance_files[0]).resolve()

    return package_file, distance_file


def parse_csv(path: str):
    """
    Parses out a csv file into a list
    :param path: str, the file location
    :return: list
    """
    try:
        with open(path, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile, dialect='excel')
            return list(reader)
    except IOError as _:
        print(f'File: {path}, was unable to be opened or does not exist.')


# calls parse_csv() on the path and modifies the returned data to create lists of vertices and edges
def parse_distance_data(path: str) -> (list, list):
    lines = parse_csv(path)

    # vertices are the addresses contained in the csv header
    v = [i.split(',\n')[1] for i in lines[0][1:]]

    # edges are represented by the weights at the column, row intersection
    # we also only care about non-null entries, so the lambda ignores things like ',,,'
    e = [list(filter(lambda x: x != "", line[1:])) for line in lines[1:]]

    return v, e


# calls parse_csv() on the path, creates packages from the data, and inserts them into a HashTable
def parse_package_data(path: str, table: structures.HashTable):
    lines = parse_csv(path)[1:]
    for row in lines:
        table.put(int(row[0]), models.Package(row))
