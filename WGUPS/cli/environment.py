import time
from pathlib import Path
from sys import stdout
from typing import Generator, Any


def get_platform() -> str:
    from sys import platform
    platforms = {
        'linux1': 'Linux',
        'linux2': 'Linux',
        'darwin': 'OS X',
        'win32': 'Windows'
    }
    if platform not in platforms:
        return platform

    return platforms[platform]


def ls(path: str, ext: str = '') -> list[Path]:
    from glob import glob
    from os.path import getmtime
    """
    Returns a list of files with the specified extension in a directory
    Orders files by most recently modified -> least recently modified
    """
    files = sorted(glob(path + '*' + ext), key=getmtime, reverse=True)
    paths = [Path(f).resolve() for f in files]
    return paths


def cls():
    print("\033[H\033[J", end="", flush=True)


def progress(it, steps: int = None, size: int = 65, file=stdout):
    """
    Display a progress bar to the user while a loop iterates
    For nested for loops, use steps to manually specify how many objects need iterated
    Args:
        it:
        steps:
        size:
        file:

    Returns:

    """
    from .style import Style
    count = len(it)

    def show(j):
        bar = f'{Style.CURSOR} {Style.END}'
        x = int(size * j / count)
        chunk = size - x
        percentage = 100 * j // count

        if steps:
            x = int(size * j * count) // steps
            chunk = size - x
            percentage = 100 * j * count // steps

        file.write("{}|{}{}| {}%{}\r".format(f' ', bar * x, ' ' * chunk, percentage, f'{Style.END}'))
        file.flush()
    show(0)

    for i, item in enumerate(it):
        yield item
        show(i + 1)
        time.sleep(0.001)
    file.write("\n")
    file.flush()
