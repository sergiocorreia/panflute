# ---------------------------
# Imports
# ---------------------------

from collections import OrderedDict, MutableSequence


# ---------------------------
# Meta Classes
# ---------------------------

class Element(object):
    """
    Base class of all Pandoc elements
    """
    __slots__ = ['parent', '_container']

    def __new__(cls, *args, **kwargs):
        # This is just to initialize self.parent to None
        element = object.__new__(cls)
        element.parent = None
        element._container = None
        return element

    @property
    def tag(self):
        tag = type(self).__name__
        return tag


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
                if val not in ([], OrderedDict(), ''):
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
        self.attributes = OrderedDict(attributes)

    def _ica_to_json(self):
        return [self.identifier, self.classes, list(self.attributes.items())]

    # ---------------------------
    # .content (setter and getter)
    # ---------------------------

    @property
    def content(self):
        """
        Sequence of :class:`Element` objects (usually either :class:`Block`
        or :class:`Inline`).

        Only available for elements that accept ``*args``.
        """
        return self._content

    @content.setter
    def content(self, value):
        oktypes = self._content.oktypes
        value = value.list if isinstance(value, Items) else list(value)
        self._content = Items(*value, oktypes=oktypes, parent=self)

    def _set_content(self, value, oktypes):
        """
        Similar to content.setter but when there are no existing oktypes
        """
        if value is None:
            value = []
        self._content = Items(*value, oktypes=oktypes, parent=self)


    # ---------------------------
    # Navigation
    # ---------------------------

    @property
    def index(self):
        """
        Return position of element inside the parent.

        If the element is TableCaption (and other corner cases), it will not
        work.

        :rtype: ``int``
        """
        if self.parent:
            return self._parent_container.index(self)

    @property
    def _parent_container(self):
        # This assumes self.parent is not None
        if self._container is None:
            return self.parent.content
        else:
            return getattr(self.parent, self._container) #  Slow??

    def offset(self, n):
        """
        Return a sibling element offset by n

        :rtype: :class:`Element` | ``None``
        """
        if self.parent:
            sibling = self.index + n
            container = self._parent_container
            if 0 <= sibling < len(container):
                return container[sibling]

    @property
    def next(self):
        """
        Return the next sibling.
        Note that ``elem.offset(1) == elem.next``

        :rtype: :class:`Element` | ``None``

        """
        return self.offset(1)

    @property
    def prev(self):
        """
        Return the previous sibling.
        Note that ``elem.offset(-1) == elem.prev``

        :rtype: :class:`Element` | ``None``
        """
        return self.offset(-1)

    def ancestor(self, n):
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


class Items(MutableSequence):
    """
    Wrapper around a list, to track the elements' parents.
    **This class shouldn't be instantiated directly by users,
    but by the elements that contain it**.

    :param args: elements contained in the list--like object
    :param oktypes: type or tuple of types that are allowed as items
    :type oktypes: ``type`` | ``tuple``
    :param parent: the parent element
    :type parent: ``Element``
    """
    # Based on http://stackoverflow.com/a/3488283
    # See also https://docs.python.org/3/library/collections.abc.html

    __slots__ = ['list', 'oktypes', 'parent', '_container']

    def __init__(self, *args, oktypes=object, parent=None):
        self.oktypes = oktypes
        self.parent = check_type(parent, (Element, type(None)))
        self._container = None
        self.list = list()
        self.extend(args)

    def __contains__(self, item):
        return item in self.list

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        self.list[i].parent = self.parent
        self.list[i]._container = self._container
        return self.list[i]

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
        return 'Items({})'.format(' '.join(repr(x) for x in self.list))

    def to_json(self):
        return [item.to_json() for item in self.list]


# ---------------------------
# Aux Functions
# ---------------------------

def encode_dict(tag, content):
    return OrderedDict((("t", tag), ("c", content)))


def check_group(value, group):
    assert not isinstance(value, Element)  # Otherwise, use check_type
    if value not in group:
        tag = type(value).__name__
        msg = 'element {} not in group {}'.format(tag, repr(group))
        raise TypeError(msg)
    else:
        return value


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
