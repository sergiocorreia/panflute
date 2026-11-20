"""
These containers keep track of the identity of the parent
object, and the attribute of the parent object that they correspond to.
"""

# ---------------------------
# Imports
# ---------------------------

from __future__ import annotations

from collections.abc import MutableSequence, MutableMapping
from itertools import chain
from typing import TYPE_CHECKING, overload
from .utils import check_type, encode_dict, debug

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator
    from typing import Any, NoReturn
    from .base import Element, MetaValue, _Action
    from .elements import Doc


# ---------------------------
# Container Classes
# ---------------------------
# These are list and dict containers that
#  (a) track the identity of their parents, and
#  (b) track the parent's property where they are stored
#  (c) track the index in the parent in case of list
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
        self.extend(args)  # self.oktypes must be set first

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
            return attach(self.list[i], self.parent, self.location, i)
        else:
            newlist = self.list.__getitem__(i)
            obj = ListContainer(*newlist,
                                oktypes=self.oktypes, parent=self.parent)
            obj.location = self.location
            return obj

    def __delitem__(self, i: int | slice) -> None:
        del self.list[i]

    @overload
    def __setitem__(self, i: int, v: Element) -> None: ...
    @overload
    def __setitem__(self, i: slice, v: Iterable[Element]) -> NoReturn: ...
    # TODO(bug-fix step): slice assignment currently always raises (attach() is
    # called on a list; see tests/test_regressions.py); once fixed, the slice
    # overload above should return None.

    def __setitem__(self, i: int | slice, v: Any) -> None:
        if isinstance(i, slice):
            v = (check_type(x, self.oktypes) for x in v)
        else:
            v = check_type(v, self.oktypes)
        self.list[i] = v
        attach(self.list[i], self.parent, self.location, i)  # type: ignore[arg-type]  # TODO(bug-fix step): wrong for slices

    def insert(self, i: int, v: Element) -> None:
        v = check_type(v, self.oktypes)
        self.list.insert(i, v)
        attach(self.list[i], self.parent, self.location, i)

    def walk(self, action: _Action, doc: Doc | None = None,
             stop_if: Callable[[Element], bool] | None = None) -> list[Element]:
        ans: Iterable[Any] = (item.walk(action, doc, stop_if) for item in self)
        # We need to convert single elements to iterables that can be flattened later
        ans = ((item,) if type(item) is not list else item for item in ans)
        # Flatten the list, by expanding any sublists
        ans = list(chain.from_iterable(ans))
        return ans

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
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

    def to_json(self) -> list[Any]:
        return [to_json_wrapper(item) for item in self.list]


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

def attach(element: Any, parent: Element | None, location: str | None, index: int | None = None) -> Any:
    if not isinstance(element, (int, str, bool)):
        element.parent = parent
        element.location = location
        element.index = index
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
