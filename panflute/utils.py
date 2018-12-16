"""
Auxiliary functions that have no dependencies
"""

# ---------------------------
# Imports
# ---------------------------

from collections import OrderedDict
import sys
import os.path as p

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
    """
    Import file or module context manager.

    * if module provided then temporarily adds extra dirs
      to sys.path and imports the module,
    * if python file provided then temporarily adds it's dir
      to sys.path and imports the file as a module.

    Example:
        >>> with ContextImport('/path/dir/fi.py', dirs) as module:
                # prepends '/path/dir' to sys.path
                # module = __import__('fi')
                module.main()
            with ContextImport('dir.fi', dirs) as module:
                # prepends dirs to sys.path
                # module = __import__('dir.fi')
                module.main()
    """
    def __init__(self, file_, extra_dirs):
        """
        :param file_: str
            full path to file or module spec. That is:
            '/' not in file, doesn't end with '.py'
        :param extra_dirs: list of str
            list of extra dirs to prepend to sys.path
            in case of file_ is a module
        """
        if not file_.endswith('.py') and not (p.sep in file_):
            self.extra_dirs = extra_dirs
            self.module = file_
        else:
            # Get the directory of the file
            self.extra_dirs = [p.dirname(file_)]
            # Get filename without .py extension:
            name, ext = p.splitext(p.basename(file_))
            self.module = name + ext.replace('.py', '')

    def __enter__(self):
        for path in reversed(self.extra_dirs):
            sys.path.insert(0, path)
        return __import__(self.module)

    def __exit__(self, exc_type, exc_value, traceback):
        for path in self.extra_dirs:
            sys.path.pop(0)
