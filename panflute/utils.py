"""
Auxiliary functions that have no dependencies
"""

# ---------------------------
# Imports
# ---------------------------

from collections import OrderedDict
import sys
import os.path as p
from importlib import import_module


# ---------------------------
# Functions
# ---------------------------


def get_caller_name():
    '''Get the name of the calling Element

    This is just the name of the Class of the __init__ calling function
    '''

    # References:
    # https://jugad2.blogspot.com/2015/09/find-caller-and-callers-caller-of.html
    # https://stackoverflow.com/a/47956089/3977107
    # https://stackoverflow.com/a/11799376/3977107

    pos = 1
    while True:
        pos += 1
        try:
            callingframe = sys._getframe(pos)
        except ValueError:
            return 'Panflute'
        #print(pos, callingframe.f_code.co_name, file=sys.stderr)

        if callingframe.f_code.co_name == '__init__':
            class_name = callingframe.f_locals['self'].__class__.__name__
            if 'Container' not in class_name:
                return class_name


def check_type(value, oktypes):
    # This allows 'Space' instead of 'Space()'
    if callable(value):
        value = value()
    
    if isinstance(value, oktypes):
        return value
    
    # Invalid type
    caller = get_caller_name()
    tag = type(value).__name__
    #oktypes_names = [x.name for x in oktypes]
    #print(oktypes, file=sys.stderr)
    msg = '\n\nElement "{}" received "{}" but expected {}\n'.format(caller, tag, oktypes)
    raise TypeError(msg)


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

class ContextImport:
    """
    Import module context manager.
    Temporarily prepends extra dir
    to sys.path and imports the module,

    Example:
        >>> # /path/dir/fi.py
        >>> with ContextImport('/path/dir/fi.py') as module:
        >>>     # prepends '/path/dir' to sys.path
        >>>     # module = import_module('fi')
        >>>     module.main()
        >>> with ContextImport('dir.fi', '/path') as module:
        >>>     # prepends '/path' to sys.path
        >>>     # module = import_module('dir.fi')
        >>>     module.main()
    """
    def __init__(self, module, extra_dir=None):
        """
        :param module: str
            module spec for import or file path
            from that only basename without .py is used
        :param extra_dir: str or None
            extra dir to prepend to sys.path
            if module then doesn't change sys.path if None
            if file then prepends dir if None
        """
        def remove_py(s):
            return s[:-3] if s.endswith('.py') else s

        self.module = remove_py(p.basename(module))
        if (extra_dir is None) and (module != p.basename(module)):
            extra_dir = p.dirname(module)
        self.extra_dir = extra_dir

    def __enter__(self):
        if self.extra_dir is not None:
            sys.path.insert(0, self.extra_dir)
        return import_module(self.module)

    def __exit__(self, exc_type, exc_value, traceback):
        if self.extra_dir is not None:
            sys.path.pop(0)
