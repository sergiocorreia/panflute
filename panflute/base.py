"""
Base classes and methods of all Pandoc elements
"""

# ---------------------------
# Imports
# ---------------------------
from __future__ import annotations

from typing import Any, TYPE_CHECKING

from operator import attrgetter
from collections.abc import MutableSequence, MutableMapping, Callable

from .containers import ListContainer, DictContainer
from .utils import check_type, encode_dict  # check_group

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import TypeVar
    from typing_extensions import Self
    from .elements import Doc
    # Type aliases are defined at the end of the module

# ---------------------------
# Meta Classes
# ---------------------------


class Element(object):
    """
    Base class of all Pandoc elements
    """
    __slots__ = ['parent', 'location', 'index_in_parent']
    _children: list[str] = []

    parent: Element | None
    location: str | None
    # Index of the element within the list that holds it, self.container
    # (the list at self.parent.<self.location>), or None when it is not held
    # in a list; set by the containers. See also the .index alias below
    index_in_parent: int | None

    # Only present on elements that take them (set by _set_ica)
    identifier: str
    classes: list[str]
    attributes: dict[str, str]

    _content: Any  # ListContainer (DictContainer for MetaMap)

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        # This is just to initialize self.parent to None
        element = object.__new__(cls)
        element.parent = None
        element.location = None
        element.index_in_parent = None
        return element

    @property
    def tag(self) -> str:
        tag = type(self).__name__
        return tag

    if TYPE_CHECKING:
        # Bound in tools.py
        def replace_keyword(self, keyword: str, replacement: Element, count: int = 0) -> Element: ...

    def __eq__(self, other: object) -> bool:
        # Doc has a different method b/c it uses __dict__ instead of slots
        if type(self) != type(other):
            return False

        for key in self.__slots__:
            if getattr(self, key) != getattr(other, key):
                return False

        return True


    # ---------------------------
    # Base methods
    # ---------------------------
    # Should be overridden except for trivial elements (Space, Null, etc.)

    def __repr__(self):
        # This is just a convenience method
        # Override it for more complex elements

        extra = []
        for key in self.__slots__:
            if not key.startswith('_') and key != 'text':
                val = getattr(self, key)
                if val not in ([], dict(), ''):
                    extra.append([key, val])

        if extra:
            extra = ('{}={}'.format(k, repr(v)) for k, v in extra)
            extra = '; ' + ', '.join(x for x in extra)
        else:
            extra = ''

        if '_content' in self.__slots__:
            content = ' '.join(repr(x) for x in self.content)
            return '{}({}{})'.format(self.tag, content, extra)
        elif 'text' in self.__slots__:
            return '{}({}{})'.format(self.tag, self.text, extra)
        else:
            return self.tag

    def to_json(self) -> Any:
        return encode_dict(self.tag, self._slots_to_json())

    def _slots_to_json(self) -> Any:
        # Default when the element contains nothing
        return []

    # ---------------------------
    # .identifier .classes .attributes
    # ---------------------------

    def _set_ica(self, identifier, classes, attributes):
        self.identifier = check_type(identifier, str)
        self.classes = [check_type(cl, str) for cl in classes]
        self.attributes = dict(attributes)

    def _ica_to_json(self):
        return [self.identifier, self.classes, list(self.attributes.items())]

    # ---------------------------
    # .content (setter and getter)
    # ---------------------------

    @property
    def content(self) -> ListContainer:
        """
        Sequence of :class:`Element` objects (usually either :class:`Block`
        or :class:`Inline`) that are "children" of the current element.

        Only available for elements that accept ``*args``.

        Note: some elements have children in attributes other than ``content``
        (such as :class:`.Table` that has children in the header and
        caption attributes).
        """
        return self._content

    @content.setter
    def content(self, value: Iterable[Element]) -> None:
        oktypes = self._content.oktypes
        # (a plain list, e.g. from walk(), needs neither a copy nor the slower
        # isinstance check against ListContainer, an abstract base class)
        if type(value) is not list:
            value = value.list if isinstance(value, ListContainer) else list(value)
        self._content = ListContainer(*value, oktypes=oktypes, parent=self)

    def _set_content(self, value: Iterable[Element] | None, oktypes: type | tuple[type, ...]) -> None:
        """
        Similar to content.setter but when there are no existing oktypes
        """
        if value is None:
            value = []
        self._content = ListContainer(*value, oktypes=oktypes, parent=self)

    # ---------------------------
    # Navigation
    # ---------------------------

    # (the index itself is the .index_in_parent slot, read and written
    # directly by the containers; .index is kept as an alias, see issue #258)
    @property
    def index(self) -> int | None:
        """
        Alias of :attr:`index_in_parent`: the index of the element within
        the list container that holds it (:attr:`container`:
        ``elem.parent.content``, or the attribute of the parent named by
        :attr:`location`), or ``None`` when no list container holds it. It can also be assigned to.

        **Not available on** :class:`.MetaList`, where ``index()`` is the
        standard sequence method (``metalist.index(value)``, as in
        ``list.index``); use ``metalist.index_in_parent`` instead.

        :rtype: ``int`` | ``None``
        """
        return self.index_in_parent

    @index.setter
    def index(self, value: int | None) -> None:
        self.index_in_parent = value

    @property
    def container(self) -> ListContainer | DictContainer | None:
        """
        Rarely used attribute that returns the ``ListContainer`` or
        ``DictContainer`` that contains the element
        (or returns None if no such container exist)

        :rtype: ``ListContainer`` | ``DictContainer`` | ``None``
        """
        if self.parent is None:
            return None
        elif self.location is None:
            return self.parent.content
        else:
            container = getattr(self.parent, self.location)
            if isinstance(container, (ListContainer, DictContainer)):
                return container
            else:
                # The element is the value of a single-element attribute
                # (e.g. Table.caption), so it is not in a container
                assert self is container  # id(self) == id(container)
                return None

    def offset(self, n: int) -> Element | None:
        """
        Return a sibling element offset by n

        :rtype: :class:`Element` | ``None``
        """

        idx = self.index_in_parent
        if idx is not None:
            sibling = idx + n
            # An element with an index_in_parent always lives in a ListContainer
            container: ListContainer = self.container  # type: ignore[assignment]
            if 0 <= sibling < len(container):
                return container[sibling]

    @property
    def next(self) -> Element | None:
        """
        Return the next sibling.
        Note that ``elem.offset(1) == elem.next``

        :rtype: :class:`Element` | ``None``

        """
        return self.offset(1)

    @property
    def prev(self) -> Element | None:
        """
        Return the previous sibling.
        Note that ``elem.offset(-1) == elem.prev``

        :rtype: :class:`Element` | ``None``
        """
        return self.offset(-1)

    def ancestor(self, n: int) -> Element | None:
        """
        Return the n-th ancestor.
        Note that ``elem.ancestor(1) == elem.parent``

        :rtype: :class:`Element` | ``None``
        """
        if not isinstance(n, int) or n < 1:
            raise TypeError('Ancestor needs to be positive, received', n)

        if n == 1 or self.parent is None:
            return self.parent
        else:
            return self.parent.ancestor(n-1)

    # ---------------------------
    # Walking
    # ---------------------------

    @property
    def doc(self) -> Doc | None:
        """
        Return the root Doc element (if there is one)

        :rtype: :class:`.Doc` | ``None``
        """
        guess: Element | None = self
        while guess is not None and guess.tag != 'Doc':
            guess = guess.parent  # If no parent, this will be None
        return guess  # type: ignore[return-value]  # Returns either Doc (tag == 'Doc') or None

    def walk(self, action: Callable[[Element, Doc], _R | None], doc: Doc | None = None,
             stop_if: Callable[[Element], bool] | None = None) -> Self | _R:
        """
        Walk through the element and all its children (sub-elements),
        applying the provided function ``action``.

        A trivial example would be:

        .. code-block:: python

            from panflute import *

            def no_action(elem, doc):
                pass

            doc = Doc(Para(Str('a')))
            altered = doc.walk(no_action)


        :param action: function that takes (element, doc) as arguments,
            and is called on every element (children first, then the
            element itself). It can return ``None`` to keep the element,
            a new element to replace it, or a list of elements to replace
            it with (an empty list ``[]`` deletes the element). Lists are
            only allowed where the element is inside a list of elements
            (e.g. not for a ``Table.caption`` or for the root element).
        :type action: :class:`function`
        :param doc: root document; used to access metadata,
            the output format (in ``.format``, other elements, and
            other variables). Only use this variable if for some reason
            you don't want to use the current document of an element.
            If not given, it is ``self.doc``, which is ``None`` when the
            element is not part of a document.
        :type doc: :class:`.Doc`
        :param stop_if: function that takes (element) as argument,
            and returns ``True`` if the children of the element should
            not be walked.
        :type stop_if: :class:`function`, optional
        :return: the element itself, unless ``action`` replaced it (in which
            case, what ``action`` returned for this element). It is never ``None``.
        :rtype: :class:`Element` | ``list`` of :class:`Element`
        """

        # Infer the document thanks to .parent magic
        if doc is None:
            doc = self.doc

        # First iterate over children; unless the stop condition is met
        if stop_if is None or not stop_if(self):

            # self._children has property *names* so we need a bit of getattr/setattr magic to modify the objects themselves
            for child_name in self._children:
                child = getattr(self, child_name)
                if isinstance(child, (Element, ListContainer, DictContainer)):
                    child = child.walk(action, doc, stop_if)
                elif child is None:
                    child = None  # Empty table headers or captions
                else:
                    raise TypeError(type(child))
                setattr(self, child_name, child)

        # Then apply the action() to the root element
        # doc is only None when walking an element that is not part of a Doc
        altered = action(self, doc)  # type: ignore[arg-type]
        return self if altered is None else altered


class Inline(Element):
    """
    Base class of all inline elements
    """
    __slots__ = []


class Block(Element):
    """
    Base class of all block elements
    """
    __slots__ = []


class MetaValue(Element):
    """
    Base class of all metadata elements
    """
    __slots__ = []


# ---------------------------
# Type aliases (only seen by type checkers)
# ---------------------------

if TYPE_CHECKING:
    # What a filter action may return for the element it receives (see Element.walk):
    # None (keep the element), an element (replace it), or a list of elements
    # (replace it with those; [] deletes it).
    _ActionResult = Element | list[Element] | None
    # A filter action, called as action(elem, doc) on every element
    _Action = Callable[[Element, Doc], _ActionResult]
    _R = TypeVar('_R', bound=Element | list[Element])
