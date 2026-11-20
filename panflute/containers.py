"""
These containers keep track of the identity of the parent
object, and the attribute of the parent object that they correspond to.
"""

# ---------------------------
# Imports
# ---------------------------

from __future__ import annotations

from collections.abc import MutableSequence, MutableMapping
from itertools import chain  # (no longer used, but part of this module's namespace)
from typing import TYPE_CHECKING, overload
from .utils import check_type, encode_dict, debug

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator
    from typing import Any
    from .base import Element, MetaValue, _Action
    from .elements import Doc


# ---------------------------
# Container Classes
# ---------------------------
# These are list and dict containers that
#  (a) track the identity of their parents, and
#  (b) track the parent's property where they are stored
#  (c) track the element's index in the list, in case of list containers
#      (the element's .index_in_parent)
# They attach these three to the elements requested through __getattr__

class ListContainer(MutableSequence["Element"]):
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

    oktypes: type | tuple[type, ...]
    parent: Element | None
    location: str | None

    def __init__(self, *args: Element, oktypes: type | tuple[type, ...]=object,
                 parent: Element | None=None) -> None:
        self.oktypes = oktypes
        self.parent = parent
        self.location = None  # Cannot be set through __init__

        self.list: list[Element] = []
        if type(self) is not ListContainer:  # (a subclass might override insert)
            self.extend(args)
            return
        # Same as self.extend(args), which calls self.insert(len(self), item)
        # for each item, but much faster (this is how every element is built)
        lst = self.list
        for i, v in enumerate(args):
            if callable(v) or not isinstance(v, oktypes):
                v = check_type(v, oktypes)
            lst.append(v)
            attach(v, parent, None, i)

    def __contains__(self, item: object) -> bool:
        return item in self.list

    def __len__(self) -> int:
        return len(self.list)

    @overload
    def __getitem__(self, i: int) -> Element: ...
    @overload
    def __getitem__(self, i: slice) -> ListContainer: ...

    def __getitem__(self, i: int | slice) -> Element | ListContainer:
        if isinstance(i, int):
            element = self.list[i]
            if i < 0:
                i += len(self.list)
            return attach(element, self.parent, self.location, i)
        else:
            return _ListSlice._from(self, self.list[i])

    def __iter__(self) -> Iterator[Element]:
        # Same as Sequence.__iter__ (``self[0]``, ``self[1]``, ... until IndexError:
        # it sees changes made to the list during the iteration, and attaches
        # each element as it is reached), without the __getitem__ calls
        i = 0
        try:
            while True:
                element = self.list[i]
                yield attach(element, self.parent, self.location, i)
                i += 1
        except IndexError:
            return

    def __delitem__(self, i: int | slice) -> None:
        del self.list[i]
        # The elements after the deleted ones have moved
        if isinstance(i, int):
            self._reindex(i if i >= 0 else i + len(self.list) + 1)
        else:
            self._reindex(0)

    @overload
    def __setitem__(self, i: int, v: Element) -> None: ...
    @overload
    def __setitem__(self, i: slice, v: Iterable[Element]) -> None: ...

    def __setitem__(self, i: int | slice, v: Any) -> None:
        if isinstance(i, slice):
            # Check every new element before changing the list
            new = [check_type(x, self.oktypes) for x in v]
            start, stop, step = i.indices(len(self.list))
            self.list[i] = new
            if step == 1:
                # The new elements are at start, start+1, ... and the
                # elements after them might have moved
                indexes = range(start, start + len(new))
                self._reindex(start + len(new))
            else:
                # Extended slice: same number of elements, nothing moves
                indexes = range(start, stop, step)
            for index_in_parent, element in zip(indexes, new):
                attach(element, self.parent, self.location, index_in_parent)
        else:
            v = check_type(v, self.oktypes)
            self.list[i] = v
            attach(v, self.parent, self.location, i if i >= 0 else i + len(self.list))

    def insert(self, i: int, v: Element) -> None:
        v = check_type(v, self.oktypes)
        # Same semantics as list.insert(): out of range indexes are clipped
        n = len(self.list)
        if i >= n:  # append (this is how containers are filled)
            self.list.append(v)
            attach(v, self.parent, self.location, n)
            return
        if i < 0:
            i = max(i + n, 0)
        self.list.insert(i, v)
        attach(v, self.parent, self.location, i)
        self._reindex(i + 1)

    def _reindex(self, start: int) -> None:
        """
        Update the ``index_in_parent`` of the elements at indexes ``start`` and
        later, after elements were inserted or removed before them.

        Elements that were last accessed through another container
        (an element can be in more than one container) are left as they are.
        """
        parent, location = self.parent, self.location
        lst = self.list
        for j in range(start, len(lst)):
            element = lst[j]
            if getattr(element, 'parent', None) is parent and getattr(element, 'location', None) == location:
                element.index_in_parent = j

    def walk(self, action: _Action, doc: Doc | None = None,
             stop_if: Callable[[Element], bool] | None = None) -> list[Element]:
        ans: list[Any] = []
        for item in self:
            walked: Any = item.walk(action, doc, stop_if)
            # Flatten the lists returned by the action
            if type(walked) is list:
                ans.extend(walked)
            else:
                ans.append(walked)
        return ans

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return 'ListContainer({})'.format(' '.join(repr(x) for x in self.list))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ListContainer):
            return NotImplemented
        # We can't compare on .parent b/c then we would get a circular reference
        if (self.oktypes != other.oktypes) or (self.location != other.location):
            return False
        if len(self.list) != len(other.list):
            return False
        for x, y in zip(self.list, other.list):  # , strict=True
            if x != y:
                return False
        return True

    def to_json(self) -> list[Any]:
        return [to_json_wrapper(item) for item in self.list]


class _ListSlice(ListContainer):
    """
    What slicing a :class:`ListContainer` returns (``elem.content[1:3]``).

    It is a new container that holds the same elements (a copy of the list,
    not a view): changing it does not change the original container.
    Neither reading nor changing it changes the ``parent``, ``location`` or
    ``index_in_parent`` of the elements, which keep describing their place in
    the original container.
    """

    __slots__ = []

    @classmethod
    def _from(cls, container: ListContainer, elements: list[Element]) -> _ListSlice:
        obj = cls.__new__(cls)
        obj.oktypes = container.oktypes
        obj.parent = container.parent
        obj.location = container.location
        obj.list = elements
        return obj

    @overload
    def __getitem__(self, i: int) -> Element: ...
    @overload
    def __getitem__(self, i: slice) -> ListContainer: ...

    def __getitem__(self, i: int | slice) -> Element | ListContainer:
        if isinstance(i, int):
            return self.list[i]
        return _ListSlice._from(self, self.list[i])

    # (not ListContainer.__iter__, which attaches the elements)
    __iter__ = MutableSequence.__iter__

    def __delitem__(self, i: int | slice) -> None:
        del self.list[i]

    @overload
    def __setitem__(self, i: int, v: Element) -> None: ...
    @overload
    def __setitem__(self, i: slice, v: Iterable[Element]) -> None: ...

    def __setitem__(self, i: int | slice, v: Any) -> None:
        if isinstance(i, slice):
            self.list[i] = [check_type(x, self.oktypes) for x in v]
        else:
            self.list[i] = check_type(v, self.oktypes)

    def insert(self, i: int, v: Element) -> None:
        self.list.insert(i, check_type(v, self.oktypes))


class DictContainer(MutableMapping[str, "MetaValue"]):
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

    oktypes: type | tuple[type, ...]
    parent: Element | None
    location: str | None

    def __init__(self, *args: tuple[str, MetaValue], oktypes: type | tuple[type, ...]=object,
                 parent: Element | None=None, **kwargs: MetaValue) -> None:
        self.oktypes = oktypes
        self.parent = parent
        self.location = None

        self.dict: dict[str, MetaValue] = dict()
        self.update(args)  # Must be a sequence of tuples
        self.update(kwargs)  # Order of kwargs is not preserved

    def __contains__(self, item: object) -> bool:
        return item in self.dict

    def __len__(self) -> int:
        return len(self.dict)

    def __getitem__(self, k: str) -> MetaValue:
        return attach(self.dict[k], self.parent, self.location)

    def __delitem__(self, k: str) -> None:
        del self.dict[k]

    def __setitem__(self, k: str, v: MetaValue) -> None:
        v = check_type(v, self.oktypes)
        self.dict[k] = v
        attach(self.dict[k], self.parent, self.location)

    def walk(self, action: _Action, doc: Doc | None = None,
             stop_if: Callable[[Element], bool] | None = None) -> list[tuple[str, Any]]:
        ans: Iterable[tuple[str, Any]] = ((k, v.walk(action, doc, stop_if)) for k, v in self.items())
        ans = [(k, v) for k, v in ans if v != []]
        return ans

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return 'DictContainer({})'.format(' '.join(repr(x) for x in self.dict))

    def __iter__(self) -> Iterator[str]:
        return self.dict.__iter__()

    def to_json(self) -> dict[str, Any]:
        return {k: to_json_wrapper(v) for k, v in self.dict.items()}


# ---------------------------
# Functions
# ---------------------------

def attach(element: Any, parent: Element | None, location: str | None, index_in_parent: int | None = None) -> Any:
    if not isinstance(element, (int, str, bool)):
        element.parent = parent
        element.location = location
        element.index_in_parent = index_in_parent
    else:
        debug(f'Warning: element "{type(element)}" has no parent')
    return element


def to_json_wrapper(e: Any) -> Any:
    if isinstance(e, str):
        return e
    elif isinstance(e, bool):
        return encode_dict('MetaBool', e)
    else:
        return e.to_json()
