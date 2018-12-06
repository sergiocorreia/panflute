"""
These containers keep track of the identity of the parent
object, and the attribute of the parent object that they correspond to.
"""

# ---------------------------
# Imports
# ---------------------------

import sys
py2 = sys.version_info[0] == 2
if py2: str = basestring

if py2:
    from collections import OrderedDict, MutableSequence, MutableMapping
else:
    from collections import OrderedDict
    from collections.abc import MutableSequence, MutableMapping
from .utils import check_type, encode_dict  # check_group


# ---------------------------
# Container Classes
# ---------------------------
# These are list and OrderedDict containers that
#  (a) track the identity of their parents, and
#  (b) track the parent's property where they are stored
# They attach these two to the elements requested through __getattr__

class ListContainer(MutableSequence):
    """
    Wrapper around a list, to track the elements' parents.
    **This class shouldn't be instantiated directly by users,
    but by the elements that contain it**.

    :param args: elements contained in the list--like object
    :param oktypes: type or tuple of types that are allowed as items
    :type oktypes: ``type`` | ``tuple``
    :param parent: the parent element
    :type parent: ``Element``
    :param container: None, unless the element is not part of its .parent.content (this is the case for table headers for instance, which are not retrieved with table.content but with table.header)
    :type container: ``str`` | None
    """
    # Based on http://stackoverflow.com/a/3488283
    # See also https://docs.python.org/3/library/collections.abc.html

    __slots__ = ['list', 'oktypes', 'parent', 'location']

    def __init__(self, *args, oktypes=object, parent=None):
        self.oktypes = oktypes
        self.parent = parent
        self.location = None  # Cannot be set through __init__

        self.list = []
        self.extend(args)  # self.oktypes must be set first

    def __contains__(self, item):
        return item in self.list

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        if isinstance(i, int):
            return attach(self.list[i], self.parent, self.location)
        else:
            newlist = self.list.__getitem__(i)
            obj = ListContainer(*newlist,
                                oktypes=self.oktypes, parent=self.parent)
            obj.location = self.location
            return obj

    def __delitem__(self, i):
        del self.list[i]

    def __setitem__(self, i, v):
        v = check_type(v, self.oktypes)
        self.list[i] = v

    def insert(self, i, v):
        v = check_type(v, self.oktypes)
        self.list.insert(i, v)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'ListContainer({})'.format(' '.join(repr(x) for x in self.list))

    def to_json(self):
        return [to_json_wrapper(item) for item in self.list]


class DictContainer(MutableMapping):
    """
    Wrapper around a dict, to track the elements' parents.
    **This class shouldn't be instantiated directly by users,
    but by the elements that contain it**.

    :param args: elements contained in the dict--like object
    :param oktypes: type or tuple of types that are allowed as items
    :type oktypes: ``type`` | ``tuple``
    :param parent: the parent element
    :type parent: ``Element``
    """

    __slots__ = ['dict', 'oktypes', 'parent', 'location']

    def __init__(self, *args, oktypes=object, parent=None, **kwargs):
        self.oktypes = oktypes
        self.parent = parent
        self.location = None

        self.dict = OrderedDict()
        self.update(args)  # Must be a sequence of tuples
        self.update(kwargs)  # Order of kwargs is not preserved

    def __contains__(self, item):
        return item in self.dict

    def __len__(self):
        return len(self.dict)

    def __getitem__(self, k):
        return attach(self.dict[k], self.parent, self.location)

    def __delitem__(self, k):
        del self.dict[k]

    def __setitem__(self, k, v):
        v = check_type(v, self.oktypes)
        self.dict[k] = v

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'DictContainer({})'.format(' '.join(repr(x) for x in self.dict))

    def __iter__(self):
        return self.dict.__iter__()

    def to_json(self):
        items = self.dict.items()
        return OrderedDict((k, to_json_wrapper(v)) for k, v in items)
        return [item.to_json() for item in self.dict]


# ---------------------------
# Functions
# ---------------------------

def attach(element, parent, location):
    if not isinstance(element, (int, str, bool)):
        element.parent = parent
        element.location = location
    else:
        print(element, 'has no parent')
    return element


def to_json_wrapper(e):
    if isinstance(e, str):
        return e
    elif isinstance(e, bool):
        return encode_dict('MetaBool', e)
    else:
        return e.to_json()
