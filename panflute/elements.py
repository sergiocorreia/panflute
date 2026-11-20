"""
Classes corresponding to Pandoc elements

Notation:
- "ica" is shorthand for "identifier, classes, attributes"
"""

# ---------------------------
# Imports
# ---------------------------

from __future__ import annotations

from typing import TYPE_CHECKING, overload

from .utils import check_type, check_group, encode_dict, decode_ica, debug, check_type_or_value
from .utils import load_pandoc_version, load_pandoc_reader_options
from .containers import ListContainer, DictContainer, MutableSequence, MutableMapping
from .base import Element, Block, Inline, MetaValue
from .table_elements import (
    Table, TableHead, TableFoot, TableBody, TableRow, TableCell, Caption,
    TABLE_ALIGNMENT, TABLE_WIDTH, table_from_json)

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Mapping
    from typing import Any, Literal

    # Values accepted by MetaList/MetaMap (and Doc metadata), converted with builtin2meta()
    _MetaInput = (MetaValue | Inline | Block | str | bool | int | float
                  | list[Any] | dict[str, Any])


# ---------------------------
# Special Root Class
# ---------------------------

# RUN ALL WITH PYCCO

class Doc(Element):
    """
    Pandoc document container.

    Besides the document, it includes the frontpage metadata and the
    desired output format. Filter functions can also add properties to it
    as means of global variables that can later be read by different calls.

    :param args: top--level documents contained in the document
    :type args: :class:`Block` sequence
    :param metadata: the frontpage metadata
    :type metadata: ``dict``
    :param format: output format, such as 'markdown', 'latex' and 'html'
    :type format: ``str``
    :param api_version: A tuple of three ints of the form (1, 18, 0)
    :type api_version: ``tuple``
    :return: Document with base class :class:`Element`
    :Base: :class:`Element`

    :Example:

        >>> meta = {'author':'John Doe'}
        >>> content = [Header(Str('Title')), Para(Str('Hello!'))]
        >>> doc = Doc(*content, metadata=meta, format='pdf')
        >>> doc.figure_count = 0 #  You can add attributes freely
    """

    _children = ['metadata', 'content']

    format: str
    api_version: tuple[int, ...]
    pandoc_version: tuple[int, ...] | None
    pandoc_reader_options: dict[str, Any]

    def __init__(self, *args: Block, metadata: Mapping[str, _MetaInput] | MetaMap = {},
                 format: str = 'html', api_version: Iterable[int] = (1, 23)) -> None:
        self._set_content(args, Block)
        self.metadata = metadata
        self.format = format  # Output format

        try:
            self.api_version = tuple(check_type(v, int) for v in api_version)
        except TypeError:
            raise TypeError(f"invalid api version {api_version!r}: expected a sequence of integers "
                            "such as (1, 23, 1), the 'pandoc-api-version' of pandoc's JSON output. "
                            "Using an older version of pandoc?") from None
        if len(self.api_version) > 4 or self.api_version[:2] < (1, 22):
            version = '.'.join(str(v) for v in self.api_version) or '(empty)'
            raise TypeError(
                f"invalid api version {version}: panflute requires pandoc API version 1.22 or "
                "later (pandoc 2.11 or later). If the document comes from pandoc, upgrade pandoc, "
                "or check which pandoc is used: convert_text() and run_pandoc() call the first "
                "`pandoc` on the PATH, which can be older than the one running the filter "
                "(e.g. the one bundled with Quarto or RStudio).")

        self.pandoc_version = load_pandoc_version()
        self.pandoc_reader_options = load_pandoc_reader_options()

    def __eq__(self, other):
        if not isinstance(other, Doc):
            return False
        if self.metadata != other.metadata:
            return False
        if self.content != other.content:
            return False
        return True

    if TYPE_CHECKING:
        # Filters can store their own attributes in the Doc (e.g. ``doc.count = 0``)
        def __getattr__(self, name: str) -> Any: ...
        def __setattr__(self, name: str, value: Any) -> None: ...

        # Bound in tools.py
        def get_metadata(self, key: str = '', default: Any = None, builtin: bool = True) -> Any: ...

    @property
    def metadata(self) -> MetaMap:
        self._metadata.parent = self
        self._metadata.location = 'metadata'
        return self._metadata

    @metadata.setter
    def metadata(self, value: Mapping[str, _MetaInput] | MetaMap) -> None:
        value = value.content if isinstance(value, MetaMap) else dict(value)
        self._metadata = MetaMap(*value.items())

    def to_json(self):
        # Overrides default method
        return {
            'pandoc-api-version': self.api_version,
            'meta': self.metadata.content.to_json(),
            'blocks': self.content.to_json(),
        }


# ---------------------------
# Classes - Empty
# ---------------------------

# TODO: Remove
class Null(Block):
    """Nothing

    :Base: :class:`Block`
    """
    __slots__ = []

    def to_json(self):
        return {'t': 'Null'}


class Space(Inline):
    """Inter-word space

    :Base: :class:`Inline`
     """
    __slots__ = []

    def to_json(self):
        return {'t': 'Space'}


class HorizontalRule(Block):
    """Horizontal rule

     :Base: :class:`Block`
     """
    __slots__ = []

    def to_json(self):
        return {'t': 'HorizontalRule'}


class SoftBreak(Inline):
    """Soft line break

     :Base: :class:`Inline`
     """
    __slots__ = []

    def to_json(self):
        return {'t': 'SoftBreak'}


class LineBreak(Inline):
    """Hard line break

     :Base: :class:`Inline`
     """
    __slots__ = []

    def to_json(self):
        return {'t': 'LineBreak'}


# ---------------------------
# Classes - Simple Containers
# ---------------------------

class Plain(Block):
    """Plain text, not a paragraph

    :param args: contents of the plain block of text
    :type args: :class:`Inline`
    :Base: :class:`Block`
    """
    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: Inline) -> None:
        self._set_content(args, Inline)

    def _slots_to_json(self):
        return self.content.to_json()


class Para(Block):
    """Paragraph

    :param args: contents of the paragraph
    :type args: :class:`Inline`
    :Base: :class:`Block`

    :Example:

        >>> content = [Str('Some'), Space, Emph(Str('words.'))]
        >>> para1 = Para(*content)
        >>> para2 = Para(Str('More'), Space, Str('words.'))
    """
    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: Inline) -> None:
        self._set_content(args, Inline)

    def _slots_to_json(self):
        return self.content.to_json()


class BlockQuote(Block):
    """Block quote

    :param args: sequence of blocks
    :type args: :class:`Block`
    :Base: :class:`Block`
     """
    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: Block) -> None:
        self._set_content(args, Block)

    def _slots_to_json(self):
        return self.content.to_json()


class Emph(Inline):
    """Emphasized text

    :param args: elements that will be emphasized
    :type args: :class:`Inline`
    :Base: :class:`Inline`
     """
    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: Inline) -> None:
        self._set_content(args, Inline)

    def _slots_to_json(self):
        return self.content.to_json()


class Strong(Inline):
    """Strongly emphasized text

    :param args: elements that will be emphasized
    :type args: :class:`Inline`
    :Base: :class:`Inline`
     """
    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: Inline) -> None:
        self._set_content(args, Inline)

    def _slots_to_json(self):
        return self.content.to_json()


class Underline(Inline):
    """Underlined text

    :param args: elements that will be underlined
    :type args: :class:`Inline`
    :Base: :class:`Inline`
     """
    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: Inline) -> None:
        self._set_content(args, Inline)

    def _slots_to_json(self):
        return self.content.to_json()


class Strikeout(Inline):
    """Strikeout text

    :param args: elements that will be striken out
    :type args: :class:`Inline`
    :Base: :class:`Inline`
     """
    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: Inline) -> None:
        self._set_content(args, Inline)

    def _slots_to_json(self):
        return self.content.to_json()


class Superscript(Inline):
    """Superscripted text (list of inlines)

    :param args: elements that will be set superscript
    :type args: :class:`Inline`
    :Base: :class:`Inline`
     """
    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: Inline) -> None:
        self._set_content(args, Inline)

    def _slots_to_json(self):
        return self.content.to_json()


class Subscript(Inline):
    """Subscripted text (list of inlines)

    :param args: elements that will be set suberscript
    :type args: :class:`Inline`
    :Base: :class:`Inline`
     """
    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: Inline) -> None:
        self._set_content(args, Inline)

    def _slots_to_json(self):
        return self.content.to_json()


class SmallCaps(Inline):
    """Small caps text (list of inlines)

    :param args: elements that will be set with small caps
    :type args: :class:`Inline`
    :Base: :class:`Inline`
     """
    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: Inline) -> None:
        self._set_content(args, Inline)

    def _slots_to_json(self):
        return self.content.to_json()


class Note(Inline):
    """Footnote or endnote

    :param args: elements that are part of the note
    :type args: :class:`Block`
    :Base: :class:`Inline`
     """
    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: Block) -> None:
        self._set_content(args, Block)

    def _slots_to_json(self):
        return self.content.to_json()


# ---------------------------
# Classes - Complex Containers
# ---------------------------

class Header(Block):
    """Header

    :param args: contents of the header
    :type args: :class:`Inline`
    :param level: level of the header (1 is the largest and 6 the smallest)
    :type level: ``int``
    :param identifier: element identifier (usually unique)
    :type identifier: :class:`str`
    :param classes: class names of the element
    :type classes: :class:`list` of :class:`str`
    :param attributes: additional attributes
    :type attributes: :class:`dict`
    :Base: :class:`Block`

    :Example:

        >>> title = [Str('Monty'), Space, Str('Python')]
        >>> header = Header(*title, level=2, identifier='toc')
        >>> header.level += 1
     """
    __slots__ = ['level', '_content', 'identifier', 'classes', 'attributes']
    _children = ['content']

    level: int

    def __init__(self, *args: Inline, level: int = 1,
                 identifier: str = '', classes: Iterable[str] = [],
                 attributes: Mapping[str, str] = {}) -> None:
        self.level = check_type(level, int)
        if not 0 < self.level <= 10:
            raise TypeError('Header level not between 1 and 10')
        self._set_ica(identifier, classes, attributes)
        self._set_content(args, Inline)

    def _slots_to_json(self):
        return [self.level, self._ica_to_json(), self.content.to_json()]


class Div(Block):
    """Generic block container with attributes

    :param args: contents of the div
    :type args: :class:`Block`
    :param identifier: element identifier (usually unique)
    :type identifier: :class:`str`
    :param classes: class names of the element
    :type classes: :class:`list` of :class:`str`
    :param attributes: additional attributes
    :type attributes: :class:`dict`
    :Base: :class:`Block`
     """

    __slots__ = ['_content', 'identifier', 'classes', 'attributes']
    _children = ['content']

    def __init__(self, *args: Block,
                 identifier: str = '', classes: Iterable[str] = [],
                 attributes: Mapping[str, str] = {}) -> None:
        self._set_ica(identifier, classes, attributes)
        self._set_content(args, Block)

    def _slots_to_json(self):
        return [self._ica_to_json(), self.content.to_json()]


class Span(Inline):
    """Generic block container with attributes

    :param args: contents of the div
    :type args: :class:`Inline`
    :param identifier: element identifier (usually unique)
    :type identifier: :class:`str`
    :param classes: class names of the element
    :type classes: :class:`list` of :class:`str`
    :param attributes: additional attributes
    :type attributes: :class:`dict`
    :Base: :class:`Inline`
     """

    __slots__ = ['_content', 'identifier', 'classes', 'attributes']
    _children = ['content']

    def __init__(self, *args: Inline,
                 identifier: str = '', classes: Iterable[str] = [],
                 attributes: Mapping[str, str] = {}) -> None:
        self._set_ica(identifier, classes, attributes)
        self._set_content(args, Inline)

    def _slots_to_json(self):
        return [self._ica_to_json(), self.content.to_json()]


class Quoted(Inline):
    """Quoted text

    :param args: contents of the quote
    :type args: :class:`Inline`
    :param quote_type: either 'SingleQuote' or 'DoubleQuote'
    :type quote_type: ``str``
    :Base: :class:`Inline`
     """

    __slots__ = ['quote_type', '_content']
    _children = ['content']

    quote_type: Literal['SingleQuote', 'DoubleQuote']

    def __init__(self, *args: Inline,
                 quote_type: Literal['SingleQuote', 'DoubleQuote'] = 'DoubleQuote') -> None:
        self.quote_type = check_group(quote_type, QUOTE_TYPES)
        self._set_content(args, Inline)

    def _slots_to_json(self):
        quote_type = {'t': self.quote_type}
        return [quote_type, self.content.to_json()]

    def _slots_to_json_legacy(self):
        quote_type = encode_dict(self.quote_type, [])
        return [quote_type, self.content.to_json()]


class Cite(Inline):
    """Cite: set of citations with related text

    :param args: contents of the cite (the raw text)
    :type args: :class:`Inline`
    :param citations: sequence of citations
    :type citations: [:class:`Citation`]
    :Base: :class:`Inline`
     """

    __slots__ = ['_content', '_citations']
    _children = ['content', 'citations']

    def __init__(self, *args: Inline, citations: Iterable[Citation] = []) -> None:
        self._set_content(args, Inline)
        self.citations = citations

    # Cannot access citations directly b/c that would mess up .parent
    @property
    def citations(self) -> ListContainer:
        return self._citations

    @citations.setter
    def citations(self, value: Iterable[Element]) -> None:
        value = value.list if isinstance(value, ListContainer) else list(value)
        self._citations = ListContainer(*value, oktypes=Citation, parent=self)
        self._citations.location = 'citations'

    def _slots_to_json(self):
        return [self.citations.to_json(), self.content.to_json()]


class Citation(Element):
    """
    A single citation to a single work

    :param id: citation key (e.g. the BibTeX keyword)
    :type id: ``str``
    :param mode: how will the citation appear ('NormalCitation' for the
        default style, 'AuthorInText' to exclude parenthesis,
        'SuppressAuthor' to exclude the author's name)
    :type mode: ``str``
    :param prefix: Text before the citation reference
    :type prefix: [:class:`Inline`]
    :param suffix: Text after the citation reference
    :type suffix: [:class:`Inline`]
    :param note_num: (Not sure...)
    :type note_num: ``int``
    :param hash: (Not sure...)
    :type hash: ``int``
    :Base: :class:`Element`
    """

    __slots__ = ['id', 'mode', '_prefix', '_suffix', 'note_num', 'hash']
    _children = ['prefix', 'suffix']

    id: str
    mode: Literal['AuthorInText', 'SuppressAuthor', 'NormalCitation']
    hash: int
    note_num: int

    def __init__(self, id: str,
                 mode: Literal['AuthorInText', 'SuppressAuthor', 'NormalCitation'] = 'NormalCitation',
                 prefix: Iterable[Inline] = (), suffix: Iterable[Inline] = (),
                 hash: int = 0, note_num: int = 0) -> None:
        self.id = check_type(id, str)
        self.mode = check_group(mode, CITATION_MODE)
        self.hash = check_type(hash, int)
        self.note_num = check_type(note_num, int)
        self.prefix = prefix
        self.suffix = suffix

    @property
    def prefix(self) -> ListContainer:
        return self._prefix

    @prefix.setter
    def prefix(self, value: Iterable[Element]) -> None:
        value = value.list if isinstance(value, ListContainer) else list(value)
        self._prefix = ListContainer(*value, oktypes=Inline, parent=self)
        self._prefix.location = 'prefix'

    @property
    def suffix(self) -> ListContainer:
        return self._suffix

    @suffix.setter
    def suffix(self, value: Iterable[Element]) -> None:
        value = value.list if isinstance(value, ListContainer) else list(value)
        self._suffix = ListContainer(*value, oktypes=Inline, parent=self)
        self._suffix.location = 'suffix'

    def to_json(self):
        # Replace default .to_json ; we don't need _slots_to_json()
        return {
            'citationSuffix': self.suffix.to_json(),
            'citationNoteNum': self.note_num,
            'citationMode': {'t': self.mode},
            'citationPrefix': self.prefix.to_json(),
            'citationId': self.id,
            'citationHash': self.hash,
        }

    def to_json_legacy(self):
        # Replace default .to_json ; we don't need _slots_to_json()
        return {
            'citationSuffix': self.suffix.to_json(),
            'citationNoteNum': self.note_num,
            'citationMode': encode_dict(self.mode, []),
            'citationPrefix': self.prefix.to_json(),
            'citationId': self.id,
            'citationHash': self.hash,
        }


class Link(Inline):
    """
    Hyperlink

    :param args: text with the link description
    :type args: :class:`Inline`
    :param url: URL or path of the link
    :type url: ``str``
    :param title: Alt. title
    :type title: ``str``
    :param identifier: element identifier (usually unique)
    :type identifier: :class:`str`
    :param classes: class names of the element
    :type classes: :class:`list` of :class:`str`
    :param attributes: additional attributes
    :type attributes: :class:`dict`
    :Base: :class:`Inline`
     """

    __slots__ = ['_content', 'url', 'title',
                 'identifier', 'classes', 'attributes']
    _children = ['content']

    url: str
    title: str

    def __init__(self, *args: Inline, url: str = '', title: str = '',
                 identifier: str = '', classes: Iterable[str] = [],
                 attributes: Mapping[str, str] = {}) -> None:
        self._set_ica(identifier, classes, attributes)
        self._set_content(args, Inline)
        self.url = check_type(url, str)
        self.title = check_type(title, str)

    def _slots_to_json(self):
        ut = [self.url, self.title]
        return [self._ica_to_json(), self.content.to_json(), ut]


class Image(Inline):
    """
    Image

    :param args: text with the image description
    :type args: :class:`Inline`
    :param url: URL or path of the image
    :type url: ``str``
    :param title: Alt. title
    :type title: ``str``
    :param identifier: element identifier (usually unique)
    :type identifier: :class:`str`
    :param classes: class names of the element
    :type classes: :class:`list` of :class:`str`
    :param attributes: additional attributes
    :type attributes: :class:`dict`
    :Base: :class:`Inline`
     """

    __slots__ = ['_content', 'url', 'title',
                 'identifier', 'classes', 'attributes']
    _children = ['content']

    url: str
    title: str

    def __init__(self, *args: Inline, url: str = '', title: str = '',
                 identifier: str = '', classes: Iterable[str] = [],
                 attributes: Mapping[str, str] = {}) -> None:
        self._set_ica(identifier, classes, attributes)
        self._set_content(args, Inline)
        self.url = check_type(url, str)
        self.title = check_type(title, str)

    def _slots_to_json(self):
        ut = [self.url, self.title]
        return [self._ica_to_json(), self.content.to_json(), ut]


# ---------------------------
# Classes - Text
# ---------------------------

class Str(Inline):
    """
    Text (a string)

    :param text: a string of unformatted text
    :type text: :class:`str`
    :Base: :class:`Inline`
     """

    __slots__ = ['text']

    text: str

    def __init__(self, text: str) -> None:
        self.text = check_type(text, str)

    def __repr__(self):
        return 'Str({})'.format(self.text)

    def _slots_to_json(self):
        return self.text


class CodeBlock(Block):
    """
    Code block (literal text) with optional attributes

    :param text: literal text (preformatted text, code, etc.)
    :type text: :class:`str`
    :param identifier: element identifier (usually unique)
    :type identifier: :class:`str`
    :param classes: class names of the element
    :type classes: :class:`list` of :class:`str`
    :param attributes: additional attributes
    :type attributes: :class:`dict`
    :Base: :class:`Block`
     """

    __slots__ = ['text', 'identifier', 'classes', 'attributes']

    text: str

    def __init__(self, text: str,
                 identifier: str = '', classes: Iterable[str] = [],
                 attributes: Mapping[str, str] = {}) -> None:
        self._set_ica(identifier, classes, attributes)
        self.text = check_type(text, str)

    def _slots_to_json(self):
        return [self._ica_to_json(), self.text]


class RawBlock(Block):
    """
    Raw block

    :param text: a string of raw text with another underlying format
    :type text: :class:`str`
    :param format: Format of the raw text ('html', 'tex', 'latex', 'context', etc.);
        any string is accepted, as in pandoc (e.g. 'comment', or the name of a custom writer)
    :type format: ``str``
    :Base: :class:`Block`
     """

    __slots__ = ['text', 'format']

    text: str
    format: str

    def __init__(self, text: str, format: str = 'html') -> None:
        self.text = check_type(text, str)
        self.format = check_type(format, str)  # Any format is valid (e.g. 'comment', custom writers)

    def _slots_to_json(self):
        return [self.format, self.text]


class Code(Inline):
    """
    Inline code (literal)

    :param text: literal text (preformatted text, code, etc.)
    :type text: :class:`str`
    :param identifier: element identifier (usually unique)
    :type identifier: :class:`str`
    :param classes: class names of the element
    :type classes: :class:`list` of :class:`str`
    :param attributes: additional attributes
    :type attributes: :class:`dict`
    :Base: :class:`Inline`
     """

    __slots__ = ['text', 'identifier', 'classes', 'attributes']

    text: str

    def __init__(self, text: str,
                 identifier: str = '', classes: Iterable[str] = [],
                 attributes: Mapping[str, str] = {}) -> None:
        self._set_ica(identifier, classes, attributes)
        self.text = check_type(text, str)

    def _slots_to_json(self):
        ica = self._ica_to_json()
        return [ica, self.text]


class Math(Inline):
    """TeX math (literal)

    :param text: a string of raw text representing TeX math
    :type text: :class:`str`
    :param format: How the math will be typeset ('DisplayMath' or 'InlineMath')
    :type format: ``str``
    :Base: :class:`Inline`
     """

    __slots__ = ['text', 'format']

    text: str
    format: Literal['DisplayMath', 'InlineMath']

    def __init__(self, text: str, format: Literal['DisplayMath', 'InlineMath'] = 'DisplayMath') -> None:
        self.text = check_type(text, str)
        self.format = check_group(format, MATH_FORMATS)

    def _slots_to_json(self):
        format = {'t': self.format}
        return [format, self.text]

    def _slots_to_json_legacy(self):
        format = encode_dict(self.format, [])
        return [format, self.text]


class RawInline(Inline):
    """Raw inline text

    :param text: a string of raw text with another underlying format
    :type text: :class:`str`
    :param format: Format of the raw text ('html', 'tex', 'latex', 'context', etc.);
        any string is accepted, as in pandoc (e.g. 'comment', or the name of a custom writer)
    :type format: ``str``
    :Base: :class:`Inline`
     """

    __slots__ = ['text', 'format']

    text: str
    format: str

    def __init__(self, text: str, format: str = 'html') -> None:
        self.text = check_type(text, str)
        self.format = check_type(format, str)  # Any format is valid (e.g. 'comment', custom writers)

    def _slots_to_json(self):
        return [self.format, self.text]


# ---------------------------
# Classes - Lists
# ---------------------------

class ListItem(Element):
    """List item (contained in bullet lists and ordered lists)

    :param args: List item
    :type args: :class:`Block`
    :Base: :class:`Element`
     """
    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: Block) -> None:
        self._set_content(args, Block)

    def to_json(self):
        return self.content.to_json()


class BulletList(Block):
    """Bullet list (unordered list)

    :param args: List item
    :type args: :class:`ListItem` | ``list``
    :Base: :class:`Block`
     """

    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: ListItem) -> None:
        self._set_content(args, ListItem)

    def _slots_to_json(self):
        return self.content.to_json()


class OrderedList(Block):
    """Ordered list (attributes and a list of items, each a list of blocks)

    :param args: List item
    :type args: :class:`ListItem` | ``list``
    :param start: Starting value of the list
    :type start: :class:`int`
    :param style: Style of the number delimiter
        ('DefaultStyle', 'Example', 'Decimal', 'LowerRoman',
        'UpperRoman', 'LowerAlpha', 'UpperAlpha')
    :type style: :class:`str`
    :param delimiter: List number delimiter
        ('DefaultDelim', 'Period', 'OneParen', 'TwoParens')
    :type delimiter: :class:`str`
    :Base: :class:`Block`
     """

    __slots__ = ['_content', 'start', 'style', 'delimiter']
    _children = ['content']

    start: int
    style: Literal['DefaultStyle', 'Example', 'Decimal', 'LowerRoman',
                   'UpperRoman', 'LowerAlpha', 'UpperAlpha']
    delimiter: Literal['DefaultDelim', 'Period', 'OneParen', 'TwoParens']

    def __init__(self, *args: ListItem, start: int = 1,
                 style: Literal['DefaultStyle', 'Example', 'Decimal', 'LowerRoman',
                                'UpperRoman', 'LowerAlpha', 'UpperAlpha'] = 'Decimal',
                 delimiter: Literal['DefaultDelim', 'Period', 'OneParen', 'TwoParens'] = 'Period') -> None:
        self._set_content(args, ListItem)
        self.start = check_type(start, int)
        self.style = check_group(style, LIST_NUMBER_STYLES)
        self.delimiter = check_group(delimiter, LIST_NUMBER_DELIMITERS)

    def _slots_to_json(self):
        style = {'t': self.style}
        delimiter = {'t': self.delimiter}
        ssd = [self.start, style, delimiter]
        return [ssd, self.content.to_json()]

    def _slots_to_json_legacy(self):
        style = encode_dict(self.style, [])
        delimiter = encode_dict(self.delimiter, [])
        ssd = [self.start, style, delimiter]
        return [ssd, self.content.to_json()]


class Definition(Element):
    """The definition (description); used in a definition list.
    It can include code and all other block elements.

    :param args: elements
    :type args: :class:`Block`
    :Base: :class:`Element`
     """
    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: Block) -> None:
        self._set_content(args, Block)

    def to_json(self):
        return self.content.to_json()


class DefinitionItem(Element):
    """
    Contains pairs of Term and Definitions (plural!)

    Each list item represents a pair of i) a term
    (a list of inlines) and ii) one or more definitions


    :param term: Term of the definition (an inline holder)
    :type term: [:class:`Inline`]
    :param definitions: List of definitions or descriptions
        (each a block holder)
    :type definition: [:class:`Definition`]
    :Base: :class:`Element`
    """
    __slots__ = ['_term', '_definitions']
    _children = ['term', 'definitions']

    def __init__(self, term: Iterable[Inline], definitions: Iterable[Definition]) -> None:
        self.term = term
        self.definitions = definitions

    def __repr__(self):
        term = self.term
        definitions = self.definitions
        return '{}({}: {})'.format(self.tag, term, definitions)

    @property
    def term(self) -> ListContainer:
        return self._term

    @term.setter
    def term(self, value: Iterable[Element]) -> None:
        value = value.list if isinstance(value, ListContainer) else list(value)
        self._term = ListContainer(*value, oktypes=Inline, parent=self)
        self._term.location = 'term'

    @property
    def definitions(self) -> ListContainer:
        return self._definitions

    @definitions.setter
    def definitions(self, value: Iterable[Element]) -> None:
        value = value.list if isinstance(value, ListContainer) else list(value)
        self._definitions = ListContainer(*value,
                                          oktypes=Definition, parent=self)
        self._definitions.location = 'definitions'

    def to_json(self):
        return [self.term.to_json(), self.definitions.to_json()]


class DefinitionList(Block):
    """Definition list: list of definition items; basically (term, definition)
    tuples.

    Each list item represents a pair of i) a term
    (a list of inlines) and ii) one or more definitions (each a list of blocks)

    Example:

        >>> term1 = [Str('Spam')]
        >>> def1 = Definition(Para(Str('...emails')))
        >>> def2 = Definition(Para(Str('...meat')))
        >>> spam = DefinitionItem(term1, [def1, def2])
        >>>
        >>> term2 = [Str('Spanish'), Space, Str('Inquisition')]
        >>> def3 = Definition(Para(Str('church'), Space, Str('court')))
        >>> inquisition = DefinitionItem(term=term2, definitions=[def3])
        >>> definition_list = DefinitionList(spam, inquisition)

    :param args: Definition items (a term with definitions)
    :type args: :class:`DefinitionItem`
    :Base: :class:`Block`
     """

    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: DefinitionItem) -> None:
        self._set_content(args, DefinitionItem)

    def _slots_to_json(self):
        return self.content.to_json()


class LineItem(Element):
    """Line item (contained in line blocks)

    :param args: Line item
    :type args: :class:`Inline`
    :Base: :class:`Element`
     """
    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: Inline) -> None:
        self._set_content(args, Inline)

    def to_json(self):
        return self.content.to_json()


class LineBlock(Block):
    """Line block (sequence of lines)

    :param args: Line item
    :type args: :class:`LineItem` | ``list``
    :Base: :class:`Block`
     """

    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: LineItem) -> None:
        self._set_content(args, LineItem)

    def _slots_to_json(self):
        return self.content.to_json()



# ---------------------------
# Classes - Figures
# ---------------------------

class Figure(Block):
    """Standalone figure, with attributes, caption, and arbitrary block content

    :param args: contents of the figure block
    :type args: :class:`Block`
    :param identifier: element identifier (usually unique)
    :type identifier: :class:`str`
    :param classes: class names of the element
    :type classes: :class:`list` of :class:`str`
    :param attributes: additional attributes
    :type attributes: :class:`dict`
    :Base: :class:`Block`

    :Example:

        >>> image = Image(Str("Description"), title='The Title',
                    url='example.png', attributes={'height':'256px'})
        >>> caption = Caption(Plain(Str('The'), Space, Str('Caption')))
        >>> figure = Figure(Plain(image), caption=caption, identifier='figure1')
     """

    __slots__ = ['_content', '_caption', 'identifier', 'classes', 'attributes']
    _children = ['content', 'caption']

    def __init__(self, *args: Block, caption: Caption | None = None,
                 identifier: str = '', classes: Iterable[str] = [],
                 attributes: Mapping[str, str] = {}) -> None:
        self._set_ica(identifier, classes, attributes)
        self._set_content(args, Block)
        self.caption = caption

    @property
    def caption(self) -> Caption:
        return self._caption

    @caption.setter
    def caption(self, value: Caption | None) -> None:
        if value is None:
            value = Caption()
        self._caption = check_type(value, Caption)
        self._caption.parent = self
        self._caption.location = 'caption'

    def _slots_to_json(self):
        return [self._ica_to_json(), self.caption.to_json(), self.content.to_json()]


# ---------------------------
# Classes - Metadata
# ---------------------------

class MetaList(MetaValue, MutableSequence[MetaValue]):
    """Metadata list container

    A :class:`MetaList` is a mutable sequence, like a ``list``:
    ``metalist.index(value)`` is the sequence method (the position of
    ``value`` in the list), not the index of the :class:`MetaList` in
    its own container as on other elements; that is
    :attr:`~.Element.index_in_parent`.

    :param args: contents of a metadata list
        (built-in values such as ``str`` or ``dict`` are converted
        to :class:`MetaValue` elements)
    :type args: :class:`MetaValue`
    :Base: :class:`MetaValue`
    """
    __slots__ = ['_content']
    _children = ['content']

    if TYPE_CHECKING:
        # Typed signature; the implementation below (which rebinds its
        # arguments) is left unannotated
        def __init__(self, *args: _MetaInput) -> None: ...
    else:
        def __init__(self, *args):
            args = [builtin2meta(v) for v in args]
            self._set_content(args, MetaValue)

    def _slots_to_json(self):
        return self.content.to_json()

    @overload
    def __getitem__(self, i: int) -> MetaValue: ...
    @overload
    def __getitem__(self, i: slice) -> MutableSequence[MetaValue]: ...

    def __getitem__(self, i: int | slice) -> MetaValue | MutableSequence[MetaValue]:
        # Slices return a ListContainer of MetaValues
        return self.content[i]  # type: ignore[return-value]

    @overload
    def __setitem__(self, i: int, v: _MetaInput) -> None: ...
    @overload
    def __setitem__(self, i: slice, v: Iterable[_MetaInput]) -> None: ...

    def __setitem__(self, i: int | slice, v: Any) -> None:
        if isinstance(i, slice):
            self.content[i] = [builtin2meta(x) for x in v]
        else:
            self.content[i] = builtin2meta(v)

    def __delitem__(self, i: int | slice) -> None:
        del self.content[i]

    def __len__(self) -> int:
        return len(self.content)

    def insert(self, i: int, v: _MetaInput) -> None:
        self.content.insert(i, builtin2meta(v))

    # On every other element, .index is an alias of .index_in_parent (the index
    # of the element in its container). A MetaList is a sequence, so here it is
    # the sequence method of MutableSequence (which remove() relies on), see
    # issue #258; the index of a MetaList in its container is .index_in_parent.
    def index(self, value: Any, start: int = 0, stop: int | None = None) -> int:  # type: ignore[override]  # a method replacing the Element.index property
        """
        Return the position of the first item equal to ``value``
        (as ``list.index``), looking only at ``metalist[start:stop]``.

        Raises ``ValueError`` if there is no such item.

        Items are compared with ``==``, and the items of a metadata list are
        :class:`MetaValue` elements (built-in values are converted when they
        are added): ``MetaList('a').index(MetaString('a')) == 0``, but
        ``MetaList('a').index('a')`` raises ``ValueError``.

        Note: on all other elements, ``elem.index`` is the index of the
        element in its container; the index of a :class:`MetaList` in its
        own container is :attr:`~.Element.index_in_parent`.
        """
        lst = self.content.list
        if stop is None:
            return lst.index(value, start)
        return lst.index(value, start, stop)

    if TYPE_CHECKING:
        # Inherited from MutableSequence (which calls insert), so they also accept builtins
        def append(self, value: _MetaInput) -> None: ...
        def extend(self, values: Iterable[_MetaInput]) -> None: ...


class MetaMap(MetaValue, MutableMapping[str, MetaValue]):
    """Metadata container for ordered dicts

    :param args: (key, value) tuples
    :type args: :class:`MetaValue`
    :param kwargs: named arguments
    :type kwargs: :class:`MetaValue`
    :Base: :class:`MetaValue`
    """
    __slots__ = ['_content']
    _children = ['content']

    if TYPE_CHECKING:
        # Typed signature; the implementation below (which rebinds its
        # arguments) is left unannotated
        def __init__(self, *args: tuple[str, _MetaInput], **kwargs: _MetaInput) -> None: ...
    else:
        def __init__(self, *args, **kwargs):
            args = list(args)
            if kwargs:
                args.extend(kwargs.items())
            args = [(k, builtin2meta(v)) for k, v in args]
            self._content = DictContainer(*args, oktypes=MetaValue, parent=self)

    def _slots_to_json(self):
        return self.content.to_json()

    # Unlike other elements, the content of a MetaMap is a mapping
    @property  # type: ignore[override]
    def content(self) -> DictContainer:
        """
        Map of :class:`MetaValue` objects.
        """
        return self._content

    @content.setter  # type: ignore[override]
    def content(self, value: Mapping[str, MetaValue] | Iterable[tuple[str, MetaValue]]) -> None:
        from collections.abc import Mapping  # (not at module level: elements is star-imported)
        items: Iterable[tuple[str, MetaValue]]
        if isinstance(value, DictContainer):
            items = value.dict.items()  # (without attaching the values to the old MetaMap)
        elif isinstance(value, Mapping):
            items = value.items()
        else:
            items = value
        self._content = DictContainer(*items, oktypes=MetaValue, parent=self)

    def __getitem__(self, i: str) -> MetaValue:
        return self.content[i]

    def __setitem__(self, i: str, v: _MetaInput) -> None:
        self.content[i] = builtin2meta(v)

    def __delitem__(self, i: str) -> None:
        del self.content[i]

    def __iter__(self) -> Iterator[str]:
        return iter(self.content)

    def __len__(self) -> int:
        return len(self.content)


class MetaInlines(MetaValue):
    """
    MetaInlines: list of arbitrary inlines within the metadata

    :param args: sequence of inline elements
    :type args: :class:`Inline`
    :Base: :class:`MetaValue`

     """

    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: Inline) -> None:
        self._set_content(args, Inline)

    def _slots_to_json(self):
        return self.content.to_json()


class MetaBlocks(MetaValue):
    """
    MetaBlocks: list of arbitrary blocks within the metadata

    :param args: sequence of block elements
    :type args: :class:`Block`
    :Base: :class:`MetaValue`
    """

    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args: Block) -> None:
        self._set_content(args, Block)

    def _slots_to_json(self):
        return self.content.to_json()


class MetaString(MetaValue):
    """
    Text (a string)

    :param text: a string of unformatted text
    :type text: :class:`str`
    :Base: :class:`MetaValue`
     """
    # Note: this is the same as the Str class but with a MetaValue parent

    __slots__ = ['text']

    text: str

    def __init__(self, text: str) -> None:
        self.text = check_type(text, str)

    def __repr__(self):
        return 'MetaString({})'.format(self.text)

    def _slots_to_json(self):
        return self.text


class MetaBool(MetaValue):
    """
    Container for True/False metadata values

    :param boolean: True/False value
    :type boolean: :class:`bool`
    :Base: :class:`MetaValue`
     """

    __slots__ = ['boolean']

    boolean: bool

    def __init__(self, boolean: bool) -> None:
        self.boolean = check_type(boolean, bool)

    def __repr__(self):
        return 'MetaBool({})'.format(self.boolean)

    def _slots_to_json(self):
        return self.boolean


# ---------------------------
# Constants
# ---------------------------

LIST_NUMBER_STYLES = {
    'DefaultStyle', 'Example', 'Decimal', 'LowerRoman',
    'UpperRoman', 'LowerAlpha', 'UpperAlpha'
}

LIST_NUMBER_DELIMITERS = {'DefaultDelim', 'Period', 'OneParen', 'TwoParens'}

QUOTE_TYPES = {'SingleQuote', 'DoubleQuote'}

CITATION_MODE = {'AuthorInText', 'SuppressAuthor', 'NormalCitation'}
# AuthorInText: @foo - as John Doe (1921) said
# SupressAuthor: [-@foo]

MATH_FORMATS = {'DisplayMath', 'InlineMath'}

# Raw formats known to pandoc (not exhaustive). Kept for reference: RawBlock and
# RawInline accept any string, as pandoc does (see issues #236 and #247).
RAW_FORMATS = {'tex',
               'latex',
               'latex-merge',  # From Quarto output.
               'html',
               'context',
               'rtf',
               'opendocument',
               'noteref',
               'openxml',
               'icml',
               'commonmark',
               'creole',
               'docbook',
               'docx',
               'dokuwiki',
               'epub',
               'fb2',
               'gfm',
               'haddock',
               'ipynb',
               'jats',
               'json',
               'man',
               'markdown',
               'markdown_github',
               'markdown_mmd',
               'markdown_phpextra',
               'markdown_strict',
               'mediawiki',
               'muse',
               'native',
               'odt',
               'opml',
               'org',
               'rst',
               't2t',
               'textile',
               'tikiwiki',
               'twiki',
               'typst',
               'vimwiki'}

SPECIAL_ELEMENTS = LIST_NUMBER_STYLES | LIST_NUMBER_DELIMITERS | \
    MATH_FORMATS | QUOTE_TYPES | CITATION_MODE | TABLE_ALIGNMENT | TABLE_WIDTH

EMPTY_ELEMENTS = {Null, Space, HorizontalRule, SoftBreak, LineBreak}


# ---------------------------
# Functions
# ---------------------------

def _decode_citation(dct):
    dct = dict(dct)  # Convert from list of tuples to dict
    return Citation(id=dct['citationId'],
                    mode=dct['citationMode'],
                    prefix=dct['citationPrefix'],
                    suffix=dct['citationSuffix'],
                    hash=dct['citationHash'],
                    note_num=dct['citationNoteNum'])


def _decode_definition_item(item):
    term, definitions = item
    definitions = [Definition(*x) for x in definitions]
    return DefinitionItem(term=term, definitions=definitions)


# _res_func is a dict from key to a function
# which is going to eat `c`
# to be used in from_json below
_res_func = {
    'Str': Str,
    'MetaBool': MetaBool,
    'MetaString': MetaString,
    # ignore c
    'Null': lambda c: Null(),
    'Space': lambda c: Space(),
    'HorizontalRule': lambda c: HorizontalRule(),
    'SoftBreak': lambda c: SoftBreak(),
    'LineBreak': lambda c: LineBreak(),
    # eat *c instead
    'Plain': lambda c: Plain(*c),
    'Para': lambda c: Para(*c),
    'BlockQuote': lambda c: BlockQuote(*c),
    'Emph': lambda c: Emph(*c),
    'Strong': lambda c: Strong(*c),
    'Underline': lambda c: Underline(*c),
    'Strikeout': lambda c: Strikeout(*c),
    'Superscript': lambda c: Superscript(*c),
    'Subscript': lambda c: Subscript(*c),
    'SmallCaps': lambda c: SmallCaps(*c),
    'Note': lambda c: Note(*c),
    'MetaList': lambda c: MetaList(*c),
    'MetaInlines': lambda c: MetaInlines(*c),
    'MetaBlocks': lambda c: MetaBlocks(*c),
    # other cases
    'Div': lambda c: Div(
        *c[1],
        **decode_ica(c[0])
    ),
    'Span': lambda c: Span(
        *c[1],
        **decode_ica(c[0])
    ),
    'Header': lambda c: Header(
        *c[2],
        level=c[0],
        **decode_ica(c[1])
    ),
    'Quoted': lambda c: Quoted(
        *c[1],
        quote_type=c[0]
    ),
    'Link': lambda c: Link(
        *c[1],
        url=c[2][0],
        title=c[2][1],
        **decode_ica(c[0])
    ),
    'Image': lambda c: Image(
        *c[1],
        url=c[2][0],
        title=c[2][1],
        **decode_ica(c[0])
    ),
    'CodeBlock': lambda c: CodeBlock(
        text=c[1],
        **decode_ica(c[0])
    ),
    'RawBlock': lambda c: RawBlock(
        text=c[1],
        format=c[0]
    ),
    'Code': lambda c: Code(
        text=c[1],
        **decode_ica(c[0])
    ),
    'Math': lambda c: Math(
        text=c[1],
        format=c[0]
    ),
    'RawInline': lambda c: RawInline(
        text=c[1],
        format=c[0]
    ),
    'Cite': lambda c: Cite(
        *c[1],
        citations=[_decode_citation(dct) for dct in c[0]]
    ),
    'BulletList': lambda c: BulletList(*[ListItem(*item) for item in c]),
    'OrderedList': lambda c: OrderedList(
        *[ListItem(*item) for item in c[1]],
        start=c[0][0],
        style=c[0][1], delimiter=c[0][2]
    ),
    'DefinitionList': lambda c: DefinitionList(*[_decode_definition_item(item) for item in c]),
    'LineBlock': lambda c: LineBlock(*[LineItem(*item) for item in c]),
    'ColWidth': lambda c: c,
    'Figure': lambda c: Figure(*c[2], caption=Caption(*c[1][1], short_caption=c[1][0]), **decode_ica(c[0])),
    'Table': table_from_json,
    'MetaMap': lambda c: MetaMap(*c.items()),
}


def from_json(data):
    # Metadata key (legacy)
    if 'unMeta' in data:
        assert len(data) == 1
        return MetaMap(*data['unMeta'].items())

    # Document (new API)
    if 'pandoc-api-version' in data:
        assert len(data) == 3
        api = data['pandoc-api-version']
        meta = data['meta']
        items = data['blocks']
        return Doc(*items, api_version=api, metadata=meta)

    # Metadata contents (including empty metadata)
    if 't' not in data:
        return data

    # Standard cases

    # Depending on the API we will have
    # - New API: ('t', 'Space')
    # - Old API: ('t', 'Space'), ('c', [])
    assert (len(data) == 1) or (len(data) == 2 and 'c' in data)
    tag = data['t']
    c = data.get('c')

    # This was slow previously because of the huge if then
    # use a dict for O(1) lookup
    if tag in _res_func:
        return _res_func[tag](c)
    elif tag in SPECIAL_ELEMENTS:
        return tag
    else:
        raise NotImplementedError(f'Unknown tag: {tag}')


# similar idea to _res_func above
# eat val
_builtin_to_meta_func = {
    Block: MetaBlocks,
    Inline: MetaInlines,
    bool: MetaBool,
    str: MetaString,
    float: lambda val: MetaString(str(val)),
    int: lambda val: MetaString(str(val)),
    list: lambda val: MetaList(*[builtin2meta(x) for x in val]),
    dict: lambda val: MetaMap(*[(k, builtin2meta(v)) for k, v in val.items()]),
}


def builtin2meta(val):
    type_ = type(val)
    if type_ in _builtin_to_meta_func:
        return _builtin_to_meta_func[type_](val)
    # support subclassed builtins. see https://github.com/sergiocorreia/panflute/issues/166
    for builtin_type, meta_func in _builtin_to_meta_func.items():
        if isinstance(val, builtin_type):
            return meta_func(val)
    return val
