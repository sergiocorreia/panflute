from functools import partial

_all__ = [
    'Null', 'HorizontalRule', 'Space', 'LineBreak', 'Str', 'Code',
    'BlockQuote', 'Note', 'Div', 'Plain', 'Para', 'Emph', 'Strong',
    'Strikeout', 'Superscript', 'Subscript', 'SmallCaps', 'Span', 'RawBlock',
    'RawInline', 'Math', 'Code', 'CodeBlock', 'Link', 'Image', 'Doc',
    'BulletList', 'OrderedList', 'DefinitionList', 'Header', 'Quoted',
    'Cite', 'Table']


# ---------------------------
# Constants
# ---------------------------

BLOCKS = {
    'Plain', 'Para', 'CodeBlock', 'RawBlock', 'BlockQuote',
    'OrderedList', 'BulletList', 'DefinitionList', 'Header',
    'HorizontalRule', 'Table', 'Div', 'Null'
}

BLOCK_CONTAINERS = {
    'BlockQuote', 'Div', 'Note'
}

HAS_ATTRIBUTES = {
    'Div', 'Span'
}

LIST_NUMBER_STYLES = {
    'DefaultStyle', 'Example', 'Decimal', 'LowerRoman',
    'UpperRoman', 'LowerAlpha', 'UpperAlpha'
}

LIST_NUMBER_DELIMITERS = {'DefaultDelim', 'Period', 'OneParen', 'TwoParens'}

TABLE_ALIGNMENT = {'AlignLeft', 'AlignRight', 'AlignCenter', 'AlignDefault'}

QUOTE_TYPES = {'SingleQuote', 'DoubleQuote'}

CITATION_MODE = {'AuthorInText', 'SuppressAuthor', 'NormalCitation'}

MATH_FORMATS = {'DisplayMath', 'InlineMath'}

RAW_FORMATS = {'html', 'latex'}


# ---------------------------
# Constructors
# ---------------------------

class ElementBase(object):
    __slots__ = ['tag']

    def __init__(self, tag):
        self.tag = tag

    def to_json(self):
        return write_dict(self.tag, [])


class ElementUnary(object):
    __slots__ = ['tag', 'text']

    def __init__(self, tag, text):
        self.tag = tag
        self.text = text

    def to_json(self):
        return write_dict(self.tag, self.text)


class ElementList(object):
    """Block and inline container with optional attributes"""
    __slots__ = ['tag', 'identifier', 'classes', 'attributes', 'items']

    def __init__(self, tag, *args,
                 identifier='', classes=None, attributes=None):
        self.tag = tag
        self.items = fix_items(args, block=self.tag in BLOCK_CONTAINERS)
        init_attr(self, identifier, classes, attributes)

    def to_json(self):
        content = [x.to_json() for x in self.items]
        if self.tag in HAS_ATTRIBUTES:
            content = [write_attr(self), content]
        return write_dict(self.tag, content)


class ElementRaw(object):
    """Container for HTML, Latex, and Math (inline and display)"""
    __slots__ = ['tag', 'format', 'math_type', 'text']

    def __init__(self, tag, text, format=None, math_type=None):
        self.tag = tag
        self.format = format
        self.text = text
        if tag == 'Math':
            assert math_type in MATH_FORMATS, math_type
        else:
            assert format in RAW_FORMATS, format
        assert isinstance(self.text, str)

    def to_json(self):
        if self.tag == 'Math':
            content = [write_dict(self.math_type, []), self.text]
        else:
            content = [self.format, self.text]

        return write_dict(self.tag, content)


class ElementTarget(object):
    __slots__ = ['tag', 'url', 'title',
                 'identifier', 'classes', 'attributes', 'items']

    def __init__(self, tag, *args, url, title='',
                 identifier='', classes=None, attributes=None):
        self.tag = tag
        self.url = url
        self.title = title
        self.items = fix_items(args, block=False)
        init_attr(self, identifier, classes, attributes)
        assert isinstance(self.url, str)
        assert isinstance(self.title, str)

    def to_json(self):
        items = [x.to_json() for x in self.items]
        target = [self.url, self.title]
        return write_dict(self.tag, [write_attr(self), items, target])


class ElementCode(object):
    __slots__ = ['tag', 'identifier', 'classes', 'attributes', 'text']

    def __init__(self, tag, text,
                 identifier='', classes=None, attributes=None):
        self.tag = tag
        self.text = text
        assert isinstance(self.text, str)
        init_attr(self, identifier, classes, attributes)

    def to_json(self):
        return write_dict(self.tag, [write_attr(self), self.text])


# ---------------------------
# Partial Elements
# ---------------------------

# Nullary elements: f() or just "f"
Null = partial(ElementBase, 'Null')
HorizontalRule = partial(ElementBase, 'HorizontalRule')
Space = partial(ElementBase, 'Space')
LineBreak = partial(ElementBase, 'LineBreak')

# Unary elements: f(text)
Str = partial(ElementUnary, 'Str')
Code = partial(ElementUnary, 'Code')

# Block holders: f(block1, block2, ...)
BlockQuote = partial(ElementList, 'BlockQuote')
Note = partial(ElementList, 'Note')
Div = partial(ElementList, 'Div')

# Inline holders: f(inline1, inline2, ...)
Plain = partial(ElementList, 'Plain')
Para = partial(ElementList, 'Para')
Emph = partial(ElementList, 'Emph')
Strong = partial(ElementList, 'Strong')
Strikeout = partial(ElementList, 'Strikeout')
Superscript = partial(ElementList, 'Superscript')
Subscript = partial(ElementList, 'Subscript')
SmallCaps = partial(ElementList, 'SmallCaps')
Span = partial(ElementList, 'Span')

# Raw container: f(format, string)
RawBlock = partial(ElementRaw, 'RawBlock')
RawInline = partial(ElementRaw, 'RawInline')
Math = partial(ElementRaw, 'Math')

# Code container
Code = partial(ElementCode, 'Code')
CodeBlock = partial(ElementCode, 'CodeBlock')

# Target containers:
Link = partial(ElementTarget, 'Link')
Image = partial(ElementTarget, 'Image')


# ---------------------------
# Standard Elements
# ---------------------------


class Doc(object):
    tag = 'Doc'

    def __init__(self, metadata=None, *args):
        self.metadata = metadata
        self.items = fix_items(args, block=True)

    def to_json(self):
        return write_dict(self.tag, [item.to_json() for item in self.items])


class BulletList(object):
    tag = 'BulletList'
    __slots__ = ['items']

    def __init__(self, *args):
        self.items = fix_items(args, block=True, depth=2)

    def to_json(self):
        content = [[x.to_json() for x in row] for row in self.items]
        return write_dict(self.tag, content)


class OrderedList(object):
    tag = 'OrderedList'
    __slots__ = ['items', 'start', 'style', 'delimiter']

    def __init__(self, *args, start=1, style='Decimal', delimiter='Period'):
        self.items = fix_items(args, block=True, depth=2)
        self.start = start
        self.style = style
        self.delimiter = delimiter

        assert (self.start == int(self.start)) and (0 <= self.start)
        assert self.style in LIST_NUMBER_STYLES, self.style
        assert self.delimiter in LIST_NUMBER_DELIMITERS, self.delimiter

    def to_json(self):

        attributes = [
            self.start,
            {"t": self.style, "c": []},
            {"t": self.delimiter, "c": []}]
        items = [[x.to_json() for x in row] for row in self.items]
        return write_dict(self.tag, [attributes, items])


class DefinitionList(object):
    # DL := List of Definitions
    # Definition := Tuple of key,value
    # Key := List of inlines
    # Value := List of blocks
    tag = 'DefinitionList'
    __slots__ = ['items']

    def __init__(self, *args):
        self.items = [(fix_items(k, block=False),
                       fix_items(v, block=True)) for k, v in args]

    def to_json(self):
        # List of tuples, each containing a list
        content = [
            [[x.to_json() for x in k], [x.to_json() for x in v]]
            for (k, v) in self.items
        ]
        return write_dict(self.tag, content)


class Header(object):
    tag = 'Header'
    __slots__ = ['level', 'identifier', 'classes', 'attributes', 'items']

    def __init__(self, *args, level=1,
                 identifier='', classes=None, attributes=None):
        self.level = level
        self.items = fix_items(args, block=False)
        init_attr(self, identifier, classes, attributes)
        assert self.level in (1, 2, 3, 4, 5, 6)

    def to_json(self):
        items = [x.to_json() for x in self.items]
        content = [self.level, write_attr(self), items]
        return write_dict(self.tag, content)


class Quoted(object):
    tag = 'Quoted'
    __slots__ = ['quote_type', 'items']

    def __init__(self, *args, quote_type):
        self.quote_type = quote_type
        self.items = fix_items(args, block=False)
        assert quote_type in QUOTE_TYPES

    def to_json(self):
        items = [x.to_json() for x in self.items]
        content = [write_dict(self.quote_type, []), items]
        return write_dict(self.tag, content)


class Cite(object):
    tag = 'Cite'
    __slots__ = ['citation', 'items']

    def __init__(self, *args, citation):
        self.citation = citation  # TODO: create Citation object
        self.items = fix_items(args, block=False)

    def to_json(self):
        items = [x.to_json() for x in self.items]
        content = [self.citation, items]
        return write_dict(self.tag, content)


class Table(object):
    tag = 'Table'
    __slots__ = ['caption', 'alignment', 'width', 'header', 'data',
                 'rows', 'cols']

    def __init__(self, data, header=None, caption=None,
                 alignment=None, width=None):
        self.data = fix_items(data, block=True, depth=3)
        self.header = fix_items(header, block=True, depth=2) \
            if header is not None else []
        self.caption = fix_items(caption, block=False) \
            if caption is not None else []
        self.rows = len(data)
        self.cols = len(data[0])
        self.alignment = ['AlignDefault'] * cols if \
            alignment is None else alignment
        self.width = [0.0] * cols if width is None else width

        assert all(item in TABLE_ALIGNMENT for item in self.alignment)
        assert all(item >= 0 for item in self.width)

        assert all(item.tag not in BLOCKS for item in self.caption)

    def to_json(self):
        caption = [x.to_json() for x in self.caption]
        header = [[block.to_json() for block in cell] for cell in self.header]
        data = [[[block.to_json() for block in cell] for cell in row]
                for row in self.data]
        alignment = [write_dict(x, []) for x in self.alignment]
        width = self.width
        content = [caption, alignment, width, header, data]
        return write_dict(self.tag, content)


# ---------------------------
# Aux Functions
# ---------------------------

def init_attr(self, identifier, classes, attributes):
    self.identifier = identifier
    self.classes = classes if classes is not None else []
    self.attributes = attributes if attributes is not None else {}
    assert isinstance(self.identifier, str)
    assert isinstance(self.attributes, dict)
    assert all(isinstance(cl, str) for cl in self.classes)


def read_attr(self, attr):
    if attr is None:
        attr = ["", [], []]  # ID, classes, attribute pairs
    self.identifier, self.classes, attributes = attr
    self.attributes = dict(attributes)


def write_attr(self):
    return [self.identifier, self.classes, list(self.attributes.items())]


def f(x, blocks):
    # BUGBUG: Slow?
    ans = x() if callable(x) else x
    assert (ans.tag in BLOCKS) if blocks else (ans not in BLOCKS)
    return ans


def fix_items(args, block, depth=1):

    assert depth in (1, 2, 3)

    if depth == 1:
        ans = tuple(f(x, block) for x in args)
    elif depth == 2:
        ans = tuple(tuple(f(x, block) for x in y) for y in args)
    else:
        ans = tuple(tuple(tuple(f(x, block) for x in y) for y in z)
                    for z in args)

    return ans


def write_dict(tag, content):
    return {"t": tag, "c": content}
