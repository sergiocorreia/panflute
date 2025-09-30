"""
Base classes and methods of all Pandoc elements
"""

# ---------------------------
# Imports
# ---------------------------
from __future__ import annotations

from panflute.containers import DictContainer, ListContainer
from typing import Any

from operator import attrgetter
from collections.abc import MutableSequence, MutableMapping, Callable

from .containers import ListContainer, DictContainer
from .utils import check_type, encode_dict  # check_group

# ---------------------------
# Meta Classes
# ---------------------------


class Element(object):
    """
    Base class of all Pandoc elements
    """
    __slots__ = ['parent', 'location', 'index']
    _children = []

    def __new__(cls, *args, **kwargs) -> Element:
        # This is just to initialize self.parent to None
        element = object.__new__(cls)
        element.parent = None
        element.location = None
        element.index = None
        return element

    @property
    def tag(self) -> str:
        tag = type(self).__name__
        return tag

    def __eq__(self, other):
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

    def to_json(self):
        return encode_dict(self.tag, self._slots_to_json())

    def _slots_to_json(self):
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
    def content(self):
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
    def content(self, value):
        oktypes: type | tuple[type] = self._content.oktypes
        value = value.list if isinstance(value, ListContainer) else list(value)
        self._content: ListContainer = ListContainer(*value, oktypes=oktypes, parent=self)

    def _set_content(self, value, oktypes):
        """
        Similar to content.setter but when there are no existing oktypes
        """
        if value is None:
            value = []
        self._content = ListContainer(*value, oktypes=oktypes, parent=self)

    # ---------------------------
    # Navigation
    # ---------------------------

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
                assert self is container  # id(self) == id(container)

    def offset(self, n: int) -> Element | None:
        """
        Return a sibling element offset by n

        :rtype: :class:`Element` | ``None``
        """

        idx = self.index
        if idx is not None:
            sibling = idx + n
            container = self.container
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
    def doc(self) -> Any | Element:
        """
        Return the root Doc element (if there is one)
        """
        guess = self
        while guess is not None and guess.tag != 'Doc':
            guess = guess.parent  # If no parent, this will be None
        return guess  # Returns either Doc or None

    def walk(self, action: Callable[[Element, Element], Any], doc: Element | None=None, stop_if=None) -> Element | None:
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


        :param action: function that takes (element, doc) as arguments.
        :type action: :class:`function`
        :param doc: root document; used to access metadata,
            the output format (in ``.format``, other elements, and
            other variables). Only use this variable if for some reason
            you don't want to use the current document of an element.
        :type doc: :class:`.Doc`
        :param stop_if: function that takes (element) as argument.
        :type stop_if: :class:`function`, optional
        :rtype: :class:`Element` | ``[]`` | ``None``
        """

        # Infer the document thanks to .parent magic
        if doc is None:
            doc = self.doc

        # First iterate over children; unless the stop condition is met
        if stop_if is None or not stop_if(self):

            # self._children has property *names* so we need a bit of getattr/setattr magic to modify the objects themselves
            children = ((child_name, getattr(self, child_name)) for child_name in self._children)

            for child_name, child in children:
                if isinstance(child, (Element, ListContainer, DictContainer)):
                    child = child.walk(action, doc, stop_if)
                elif child is None:
                    child = None  # Empty table headers or captions
                else:
                    raise TypeError(type(child))
                setattr(self, child_name, child)

        # Then apply the action() to the root element
        altered = action(self, doc)
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
