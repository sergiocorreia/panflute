# ---------------------------
# Imports
# ---------------------------

from collections import OrderedDict

from .utils import check_type, check_group, encode_dict
from .containers import ListContainer, DictContainer
from .base import Element, Block, Inline, MetaValue

import sys
py2 = sys.version_info[0] == 2
if py2: str = basestring


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

    def __init__(self, *args, metadata={}, format='html', api_version=None):
        self._set_content(args, Block)
        self.metadata = metadata
        self.format = format  # Output format

        # Handle Pandoc Legacy
        if api_version is None:
            self.api_version = None  # Pandoc Legacy
        elif len(api_version) > 4:
            raise TypeError("invalid api version", api_version)
        elif tuple(api_version) <= (1, 17, 0):
            raise TypeError("invalid api version", api_version)
        else:
            self.api_version = tuple(check_type(v, int) for v in api_version)

    @property
    def metadata(self):
        self._metadata.parent = self
        self._metadata.location = 'metadata'
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        if isinstance(value, MetaMap):
            value = value.content
        else:
            value = OrderedDict(value)
        self._metadata = MetaMap(*value.items())

    def to_json(self):
        # Overrides default method
        meta = self.metadata.content.to_json()
        blocks = self.content.to_json()

        if self.api_version is None:
            return [{'unMeta': meta}, blocks]
        else:
            ans = OrderedDict()
            ans['pandoc-api-version'] = self.api_version
            ans['meta'] = meta
            ans['blocks'] = blocks
            return ans


# ---------------------------
# Classes - Empty
# ---------------------------

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

    def __init__(self, *args):
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

    def __init__(self, *args):
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

    def __init__(self, *args):
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

    def __init__(self, *args):
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

    def __init__(self, *args):
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

    def __init__(self, *args):
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

    def __init__(self, *args):
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

    def __init__(self, *args):
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

    def __init__(self, *args):
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

    def __init__(self, *args):
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

    def __init__(self, *args, level=1,
                 identifier='', classes=[], attributes={}):
        self.level = check_type(level, int)
        if not 0 < self.level <= 6:
            raise TypeError('Header level not between 1 and 6')
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

    def __init__(self, *args, identifier='', classes=[], attributes={}):
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

    def __init__(self, *args, identifier='', classes=[], attributes={}):
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

    def __init__(self, *args, quote_type='DoubleQuote'):
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

    def __init__(self, *args, citations=[]):
        self._set_content(args, Inline)
        self.citations = citations

    # Cannot access citations directly b/c that would mess up .parent
    @property
    def citations(self):
        return self._citations

    @citations.setter
    def citations(self, value):
        value = value.list if isinstance(value, ListContainer) else list(value)
        self._citations = ListContainer(*value, oktypes=Citation, parent=self)
        self._citations.location = 'citations'

    def _slots_to_json(self):
        return [self.citations.to_json(), self.content.to_json()]


class Citation(Element):
    """
    A single citation to a single work

    :param id: citation key (e.g. the bibtex keyword)
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

    def __init__(self, id, mode='NormalCitation', prefix='', suffix='',
                 hash=0, note_num=0):
        self.id = check_type(id, str)
        self.mode = check_group(mode, CITATION_MODE)
        self.hash = check_type(hash, int)
        self.note_num = check_type(note_num, int)
        self.prefix = prefix
        self.suffix = suffix

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, value):
        value = value.list if isinstance(value, ListContainer) else list(value)
        self._prefix = ListContainer(*value, oktypes=Inline, parent=self)
        self._prefix.location = 'prefix'

    @property
    def suffix(self):
        return self._suffix

    @suffix.setter
    def suffix(self, value):
        value = value.list if isinstance(value, ListContainer) else list(value)
        self._suffix = ListContainer(*value, oktypes=Inline, parent=self)
        self._suffix.location = 'suffix'

    def to_json(self):
        # Replace default .to_json ; we don't need _slots_to_json()
        ans = OrderedDict()
        ans['citationSuffix'] = self.suffix.to_json()
        ans['citationNoteNum'] = self.note_num
        ans['citationMode'] = {'t': self.mode}
        ans['citationPrefix'] = self.prefix.to_json()
        ans['citationId'] = self.id
        ans['citationHash'] = self.hash
        return ans

    def to_json_legacy(self):
        # Replace default .to_json ; we don't need _slots_to_json()
        ans = OrderedDict()
        ans['citationSuffix'] = self.suffix.to_json()
        ans['citationNoteNum'] = self.note_num
        ans['citationMode'] = encode_dict(self.mode, [])
        ans['citationPrefix'] = self.prefix.to_json()
        ans['citationId'] = self.id
        ans['citationHash'] = self.hash
        return ans


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

    def __init__(self, *args, url='', title='',
                 identifier='', classes=[], attributes={}):
        self._set_content(args, Inline)
        self._set_ica(identifier, classes, attributes)
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

    def __init__(self, *args, url='', title='',
                 identifier='', classes=[], attributes={}):
        self._set_content(args, Inline)
        self._set_ica(identifier, classes, attributes)
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

    def __init__(self, text):
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

    def __init__(self, text, identifier='', classes=[], attributes={}):
        self.text = check_type(text, str)
        self._set_ica(identifier, classes, attributes)

    def _slots_to_json(self):
        return [self._ica_to_json(), self.text]


class RawBlock(Block):
    """
    Raw block

    :param text: a string of raw text with another underlying format
    :type text: :class:`str`
    :param format: Format of the raw text ('html', 'tex', 'latex' or 'context')
    :type format: ``str``
    :Base: :class:`Block`
     """

    __slots__ = ['text', 'format']

    def __init__(self, text, format='html'):
        self.text = check_type(text, str)
        self.format = check_group(format, RAW_FORMATS)

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

    def __init__(self, text, identifier='', classes=[], attributes={}):
        self.text = check_type(text, str)
        self._set_ica(identifier, classes, attributes)

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

    def __init__(self, text, format='DisplayMath'):
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
    :param format: Format of the raw text ('html', 'tex', 'latex' or 'context')
    :type format: ``str``
    :Base: :class:`Inline`
     """

    __slots__ = ['text', 'format']

    def __init__(self, text, format='html'):
        self.text = check_type(text, str)
        self.format = check_group(format, RAW_FORMATS)

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

    def __init__(self, *args):
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

    def __init__(self, *args):
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

    def __init__(self, *args, start=1, style='Decimal', delimiter='Period'):
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

    def __init__(self, *args):
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

    def __init__(self, term, definitions):
        self.term = term
        self.definitions = definitions

    def __repr__(self):
        term = self.term
        definitions = self.definitions
        return '{}({}: {})'.format(self.tag, term, definitions)

    @property
    def term(self):
        return self._term

    @term.setter
    def term(self, value):
        value = value.list if isinstance(value, ListContainer) else list(value)
        self._term = ListContainer(*value, oktypes=Inline, parent=self)
        self._term.location = 'term'

    @property
    def definitions(self):
        return self._definitions

    @definitions.setter
    def definitions(self, value):
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

    def __init__(self, *args):
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

    def __init__(self, *args):
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

    def __init__(self, *args):
        self._set_content(args, LineItem)

    def _slots_to_json(self):
        return self.content.to_json()


class TableCell(Element):
    """
    Table Cell

    :param args: elements
    :type args: :class:`Block`
    :Base: :class:`Element`
     """
    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args):
        self._set_content(args, Block)

    def to_json(self):
        return self.content.to_json()


class TableRow(Element):
    """
    Table Row

    :param args: cells
    :type args: :class:`TableCell`
    :Base: :class:`Element`
     """
    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args):
        self._set_content(args, TableCell)

    def to_json(self):
        return self.content.to_json()


class Table(Block):
    """Table, made by a list of table rows, and
    with optional caption, column alignments, relative column widths and
    column headers.

    Example:

        >>> x = [Para(Str('Something')), Para(Space, Str('else'))]
        >>> c1 = TableCell(*x)
        >>> c2 = TableCell(Header(Str('Title')))
        >>>
        >>> rows = [TableRow(c1, c2)]
        >>> table = Table(*rows, header=TableRow(c2,c1))

    :param args: Table rows
    :type args: :class:`TableRow`
    :param header: A special row specifying the column headers
    :type header: :class:`TableRow`
    :param caption: The caption of the table
    :type caption: [:class:`Inline`]
    :param alignment: List of row alignments
        (either 'AlignLeft', 'AlignRight', 'AlignCenter' or 'AlignDefault').
    :type alignment: [:class:`str`]
    :param width: Relative column widths (default is a list of 0.0s)
    :type width: [:class:`float`]
    :Base: :class:`Block`
     """

    __slots__ = ['_content', '_header', '_caption',
                 'alignment', 'width', 'rows', 'cols']
    _children = ['header', 'content', 'caption']

    def __init__(self, *args, header=None, caption=None,
                 alignment=None, width=None):

        self._set_content(args, TableRow)
        self.rows = len(self.content)
        self.cols = len(self.content[0].content)
        self.header = header
        self.caption = caption if caption else []

        if alignment is None:
            self.alignment = ['AlignDefault'] * self.cols
        else:
            self.alignment = [check_group(a, TABLE_ALIGNMENT)
                              for a in alignment]
            if len(self.alignment) != self.cols:
                raise IndexError('alignment has an incorrect number of cols')

        if width is None:
            self.width = [0.0] * self.cols
        else:
            self.width = [check_type(w, (float, int)) for w in width]
            if len(self.width) != self.cols:
                raise IndexError('width has an incorrect number of cols')

    @property
    def header(self):
        if self._header is not None:
            self._header.parent = self
            self._header.location = 'header'
        return self._header

    @header.setter
    def header(self, value):
        if not value or (isinstance(value, TableRow) and not value.content):
            self._header = None
            return

        value = value.content if isinstance(value, TableRow) else list(value)
        self._header = TableRow(*value)
        if len(value) != self.cols:
            msg = 'table header has an incorrect number of cols:'
            msg += ' {} rows but expected {}'.format(len(value), self.cols)
            raise IndexError(msg)

    @property
    def caption(self):
        return self._caption

    @caption.setter
    def caption(self, value):
        value = value.list if isinstance(value, ListContainer) else list(value)
        self._caption = ListContainer(*value, oktypes=Inline, parent=self)
        self._caption.location = 'caption'

    def _slots_to_json(self):
        caption = [chunk.to_json() for chunk in self.caption]
        alignment = [{'t': x} for x in self.alignment]
        if self.header is None:
            header = [[]] * self.cols
        else:
            header = self.header.to_json()
        items = self.content.to_json()
        content = [caption, alignment, self.width, header, items]
        return content

    def _slots_to_json_legacy(self):
        caption = [chunk.to_json() for chunk in self.caption]
        alignment = [encode_dict(x, []) for x in self.alignment]
        if self.header is None:
            header = [[]] * self.cols
        else:
            header = self.header.to_json()
        items = self.content.to_json()
        content = [caption, alignment, self.width, header, items]
        return content


class MetaList(MetaValue):
    """Metadata list container

    :param args: contents of a metadata list
    :type args: :class:`MetaValue`
    :Base: :class:`MetaValue`
    """
    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args):
        args = [builtin2meta(v) for v in args]
        self._set_content(args, MetaValue)

    def _slots_to_json(self):
        return self.content.to_json()

    def __getitem__(self, i):
        return self.content[i]

    def __setitem__(self, i, v):
        self.content[i] = builtin2meta(v)

    def append(self, i):
        self.content.append(i)


class MetaMap(MetaValue):
    """Metadata container for ordered dicts

    :param args: (key, value) tuples
    :type args: :class:`MetaValue`
    :param kwargs: named arguments
    :type kwargs: :class:`MetaValue`
    :Base: :class:`MetaValue`
    """
    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args, **kwargs):
        args = list(args)
        if kwargs:
            args.extend(kwargs.items())
        args = [(k, builtin2meta(v)) for k, v in args]
        self._content = DictContainer(*args, oktypes=MetaValue, parent=self)

    def _slots_to_json(self):
        return self.content.to_json()

    # ---------------------------
    # replace .content container (ListContainer to DictContainer)
    # ---------------------------

    @property
    def content(self):
        """
        Map of :class:`MetaValue` objects.
        """
        return self._content

    @content.setter
    def content(self, value):
        if isinstance(value, dict):
            value = value.dict.items()
        self._content = DictContainer(*value, oktypes=MetaValue, parent=self)

    # These two are convenience functions, not sure if really needed...
    # (they save typing the .content and converting to metavalues)
    def __getitem__(self, i):
        return self.content[i]

    def __setitem__(self, i, v):
        self.content[i] = builtin2meta(v)

    def __contains__(self, i):
        return i in self.content


class MetaInlines(MetaValue):
    """
    MetaInlines: list of arbitrary inlines within the metadata

    :param args: sequence of inline elements
    :type args: :class:`Inline`
    :Base: :class:`MetaValue`

     """

    __slots__ = ['_content']
    _children = ['content']

    def __init__(self, *args):
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

    def __init__(self, *args):
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

    def __init__(self, text):
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

    def __init__(self, boolean):
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

TABLE_ALIGNMENT = {'AlignLeft', 'AlignRight', 'AlignCenter', 'AlignDefault'}

QUOTE_TYPES = {'SingleQuote', 'DoubleQuote'}

CITATION_MODE = {'AuthorInText', 'SuppressAuthor', 'NormalCitation'}
# AuthorInText: @foo - as John Doe (1921) said
# SupressAuthor: [-@foo]

MATH_FORMATS = {'DisplayMath', 'InlineMath'}

RAW_FORMATS = {'html', 'tex', 'latex', 'context', 'rtf', 'opendocument',
               'noteref', 'openxml', 'icml'}

SPECIAL_ELEMENTS = LIST_NUMBER_STYLES | LIST_NUMBER_DELIMITERS | \
    MATH_FORMATS | TABLE_ALIGNMENT | QUOTE_TYPES | CITATION_MODE

EMPTY_ELEMENTS = {Null, Space, HorizontalRule, SoftBreak, LineBreak}


# ---------------------------
# Functions
# ---------------------------

def _decode_ica(lst):
    return {'identifier': lst[0],
            'classes': lst[1],
            'attributes': lst[2]}


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


def _decode_row(row):
    row = [TableCell(*x) for x in row]
    return TableRow(*row)


def from_json(data):

    # OrderedDict should be fast in 3.6+, so don't worry about speed:
    # https://twitter.com/raymondh/status/773978885092323328
    data = OrderedDict(data)

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

    # Maybe using globals() is too slow?
    # TODO: Try w/out globals, as json.load() is a bit slow

    if tag == 'Str':
        return Str(c)

    elif tag in ('Null', 'Space', 'HorizontalRule', 'SoftBreak', 'LineBreak'):
        return globals()[tag]()

    elif tag in ('Plain', 'Para', 'BlockQuote', 'Emph', 'Strong', 'Strikeout',
                 'Superscript', 'Subscript', 'SmallCaps', 'Note'):
        return globals()[tag](*c)

    elif tag in ('Div', 'Span'):
        return globals()[tag](*c[1], **_decode_ica(c[0]))

    elif tag == 'Header':
        return Header(*c[2], level=c[0], **_decode_ica(c[1]))

    elif tag == 'Quoted':
        return Quoted(*c[1], quote_type=c[0])

    elif tag == 'Link':
        return Link(*c[1], url=c[2][0], title=c[2][1], **_decode_ica(c[0]))

    elif tag == 'Image':
        return Image(*c[1], url=c[2][0], title=c[2][1], **_decode_ica(c[0]))

    elif tag == 'CodeBlock':
        return CodeBlock(text=c[1], **_decode_ica(c[0]))

    elif tag == 'RawBlock':
        return RawBlock(text=c[1], format=c[0])

    elif tag == 'Code':
        return Code(text=c[1], **_decode_ica(c[0]))

    elif tag == 'Math':
        return Math(text=c[1], format=c[0])

    elif tag == 'RawInline':
        return RawInline(text=c[1], format=c[0])

    elif tag == 'Cite':
        items = [_decode_citation(dct) for dct in c[0]]
        return Cite(*c[1], citations=items)

    elif tag == 'BulletList':
        items = [ListItem(*item) for item in c]
        return BulletList(*items)

    elif tag == 'OrderedList':
        items = [ListItem(*item) for item in c[1]]
        return OrderedList(*items, start=c[0][0],
                           style=c[0][1], delimiter=c[0][2])

    elif tag == 'DefinitionList':
        items = [_decode_definition_item(item) for item in c]
        return DefinitionList(*items)

    elif tag == 'LineBlock':
        items = [LineItem(*item) for item in c]
        return LineBlock(*items)

    elif tag == 'Table':
        header = _decode_row(c[3])
        data = [_decode_row(x) for x in c[4]]
        return Table(*data, caption=c[0], alignment=c[1], width=c[2],
                     header=header)

    elif tag == 'MetaList':
        return MetaList(*c)

    elif tag == 'MetaMap':
        return MetaMap(*c.items())

    elif tag == 'MetaInlines':
        return MetaInlines(*c)

    elif tag == 'MetaBlocks':
        return MetaBlocks(*c)

    elif tag == 'MetaString':
        return MetaString(c)

    elif tag == 'MetaBool':
        assert c in {True, False}, c
        return MetaBool(c)

    elif tag in SPECIAL_ELEMENTS:
        return tag

    else:
        raise Exception('unknown tag: ' + tag)


def builtin2meta(val):
    if isinstance(val, bool):
        return MetaBool(val)
    elif isinstance(val, (float, int)):
        return MetaString(str(val))
    elif isinstance(val, list):
        return MetaList(*val)
    elif isinstance(val, dict):
        return MetaMap(*val.items())
    elif isinstance(val, Block):
        return MetaBlocks(val)
    elif isinstance(val, Inline):
        return MetaInlines(val)
    else:
        return val
