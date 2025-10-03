"""
These containers keep track of the identity of the parent
object, and the attribute of the parent object that they correspond to.
"""

# ---------------------------
# Imports
# ---------------------------

from collections.abc import MutableSequence, MutableMapping
from itertools import chain
from .utils import check_type, encode_dict, debug


# ---------------------------
# Container Classes
# ---------------------------
# These are list and dict containers that
#  (a) track the identity of their parents, and
#  (b) track the parent's property where they are stored
#  (c) track the index in the parent in case of list
# They attach these three to the elements requested through __getattr__

class ListContainer(MutableSequence[object]):
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

    def __init__(self, *args: MutableSequence[object], oktypes: type | tuple[type]=object, parent: object | None=None):
        self.oktypes: type | tuple[type] = oktypes
        self.parent: object | None = parent
        self.location = None  # Cannot be set through __init__

        self.list = []
        self.extend(args)  # self.oktypes must be set first

    def __contains__(self, item):
        return item in self.list

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        if isinstance(i, int):
            return attach(self.list[i], self.parent, self.location, i)
        else:
            newlist = self.list.__getitem__(i)
            obj = ListContainer(*newlist,
                                oktypes=self.oktypes, parent=self.parent)
            obj.location = self.location
            return obj

    def __delitem__(self, i):
        del self.list[i]

    def __setitem__(self, i, v):
        if isinstance(i, slice):
            v = (check_type(x, self.oktypes) for x in v)
        else:
            v = check_type(v, self.oktypes)
        self.list[i] = v
        attach(self.list[i], self.parent, self.location, i)

    def insert(self, i: int, v):
        v = check_type(v, self.oktypes)
        self.list.insert(i, v)
        attach(self.list[i], self.parent, self.location, i)

    def walk(self, action, doc=None, stop_if=None):
        ans = (item.walk(action, doc, stop_if) for item in self)
        # We need to convert single elements to iterables that can be flattened later
        ans = ((item,) if type(item) is not list else item for item in ans)
        # Flatten the list, by expanding any sublists
        ans = list(chain.from_iterable(ans))
        return ans

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'ListContainer({})'.format(' '.join(repr(x) for x in self.list))

    def __eq__(self, other):
        # We can't compare on .parent b/c then we would get a circular reference
        if (self.oktypes != other.oktypes) or (self.location != other.location):
            return False
        if len(self.list) != len(other.list):
            return False
        for x, y in zip(self.list, other.list):  # , strict=True
            if x != y:
                return False
        return True

    def to_json(self):
        return [to_json_wrapper(item) for item in self.list]


class DictContainer(MutableMapping[str, object]):
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

    def __init__(self, *args: MutableMapping[str, object], oktypes: type | tuple[type]=object, parent: Element | None=None, **kwargs):
        self.oktypes: type | tuple[type] = oktypes
        self.parent: object | None = parent
        self.location = None

        self.dict = dict()
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
        attach(self.dict[k], self.parent, self.location)

    def walk(self, action, doc=None, stop_if=None):
        ans = ((k, v.walk(action, doc, stop_if)) for k, v in self.items())
        ans = [(k, v) for k, v in ans if v != []]
        return ans

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'DictContainer({})'.format(' '.join(repr(x) for x in self.dict))

    def __iter__(self):
        return self.dict.__iter__()

    def to_json(self):
        return {k: to_json_wrapper(v) for k, v in self.dict.items()}


# ---------------------------
# Functions
# ---------------------------

def attach(element, parent, location, index=None):
    if not isinstance(element, (int, str, bool)):
        element.parent = parent
        element.location = location
        element.index = index
    else:
        debug(f'Warning: element "{type(element)}" has no parent')
    return element


def to_json_wrapper(e):
    if isinstance(e, str):
        return e
    elif isinstance(e, bool):
        return encode_dict('MetaBool', e)
    else:
        return e.to_json()
