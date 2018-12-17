"""
Auxiliary functions that have no dependencies
"""

# ---------------------------
# Imports
# ---------------------------

from collections import OrderedDict
import sys
import os.path as p
import re

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
rstrip_py = re.compile(r'\.py$')


class ContextImport():
    """
    Import module context manager.
    Temporarily prepends extra dir
    to sys.path and imports the module,

    Example:
        >>> # /path/dir/fi.py
        >>> with ContextImport('fi', '/path/dir') as module:
                # prepends '/path/dir' to sys.path
                # module = __import__('fi')
                module.main()
            with ContextImport('dir.fi', '/path') as module:
                # prepends '/path' to sys.path
                # module = __import__('dir.fi')
                module.main()
    """
    def __init__(self, module, extra_dir):
        """
        :param module: str
            module spec for import or file path
            from that only basename without .py is used
        :param extra_dir: str or None
            extra dir to prepend to sys.path
            doesn't change sys.path if None
        """
        self.extra_dir = extra_dir
        self.module = rstrip_py.sub('', p.basename(module))

    def __enter__(self):
        if self.extra_dir is not None:
            sys.path.insert(0, self.extra_dir)
        return __import__(self.module)

    def __exit__(self, exc_type, exc_value, traceback):
        if self.extra_dir is not None:
            sys.path.pop(0)
