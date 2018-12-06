"""
Auxiliary functions that have no dependencies
"""

# ---------------------------
# Imports
# ---------------------------

from collections import OrderedDict
import sys

# ---------------------------
# Functions
# ---------------------------

def check_type(value, oktypes):
    # This allows 'Space' instead of 'Space()'
    if callable(value):
        value = value()
    if not isinstance(value, oktypes):
        tag = type(value).__name__
        msg = 'received {} but expected {}'.format(tag, oktypes)
        raise TypeError(msg)
    else:
        return value


def check_group(value, group):
    if value not in group:
        tag = type(value).__name__
        msg = 'element {} not in group {}'.format(tag, repr(group))
        raise TypeError(msg)
    else:
        return value


def encode_dict(tag, content):
    return OrderedDict((("t", tag), ("c", content)))

# ---------------------------
# Classes
# ---------------------------


class ContextImport():
    """Import File Context Manager
    Adds temporarly the director of zed file to the path, and puts in context
    the file.
    :params file: Full path to file with extension
    :type file: `str`

    :Example:
        >>> filename = 'foo.py'[:-3] # With out py extension
        >>> with add_path('/path/to/dir'):
                modules = __import__(filename)
                bar = module.bar
                baz = module.baz
        >>> baz()
        >>> print(bar)
    """
    def __init__(self, file):
        # Get the directory of the file
        self.path = r"/".join(file.split(r"/")[:-1])
        # Get filename without extension
        self.file = file.split(r"/")[-1].replace(".py", "")

    def __enter__(self):
        sys.path.insert(0, self.path)
        return __import__(self.file)

    def __exit__(self, exc_type, exc_value, traceback):
        sys.path.remove(self.path)
