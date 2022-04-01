import signal
import sys

from core.hub import Hub
from models import Address, Coordinate, Package, Truck
from structures import Graph, HashTable


def _signal_handler(sig, frame):
    print("\nCtrl-C was pressed. Exiting ...")
    sys.exit(0)


class App:
    def __init__(self, hub: Hub):
        self.hub = hub

    def run(self):
        signal.signal(signal.SIGINT, _signal_handler)

        while True:
            # TODO: do processing
            pass
