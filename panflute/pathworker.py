"""
Auxiliary classes that have no dependencies.
"""

# ---------------------------
# Imports
# ---------------------------

import sys

# ---------------------------
# Classes 
# ---------------------------


class context_import():
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
        self.file = file.split(r"/")[-1][:-3]


    def __enter__(self):
        sys.path.insert(0, self.path)
        return __import__(self.file)
        

    def __exit__(self, exc_type, exc_value, traceback):
        sys.path.remove(self.path)
