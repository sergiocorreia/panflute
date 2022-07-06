"""
Classes corresponding to Pandoc Table elements
"""


# ---------------------------
# Imports
# ---------------------------

from .utils import decode_ica, check_group, check_type, check_type_or_value, encode_dict, debug
from .containers import ListContainer
from .base import Element, Block, Inline


# ---------------------------
# Classes
# ---------------------------

class Table(Block):
    """Table, composed of a table head, one or more table bodies, and a
    a table foot. You can also specify captions, short captions, column alignments,
    and column widths.

    Example:

        >>> x = [Para(Str('Something')), Para(Space, Str('else'))]
        >>> c1 = TableCell(*x)
        >>> c2 = TableCell(Header(Str('Title')))
        >>> row = TableRow(c1, c2)
        >>>
        >>> body = TableBody(row)
        >>> head = TableHead(row)
        >>> caption = Caption(Para(Str('Title')))
        >>> table = Table(body, head=head, caption=caption)

    TODO: UPDATE EXAMPLE
    TODO: OFFER A SIMPLE WAY TO BUILD A TABLE, with e.g. .alignments and .widths

    :param args: Table bodies
    :type args: :class:`TableBody`
    :param head: Table head
    :type head: :class:`TableHead`
    :param foot: Table foot
    :type foot: :class:`TableFoot`
    :param caption: The caption of the table (with optional short caption)
    :type caption: :class:`Caption`
    :param colspec: list of (alignment, colwidth) tuples; one for each column
    :type colspec: :class:`list` of (:class:`Alignment`, :class:`ColWidth`)
    :param identifier: element identifier (usually unique)
    :type identifier: :class:`str`
    :param classes: class names of the element
    :type classes: :class:`list` of :class:`str`
    :param attributes: additional attributes
    :type attributes: :class:`dict`
    :Base: :class:`Block`

    :param alignment: List of row alignments
        (either 'AlignLeft', 'AlignRight', 'AlignCenter' or 'AlignDefault').
    :type alignment: [:class:`str`]

    :param colwidth: Fractional column widths
    :type colwidth: [:class:`float` | "ColWidthDefault"]
     """

    __slots__ = ['_content', '_head', '_foot', '_caption', 'colspec',
                 'identifier', 'classes', 'attributes', 'cols']
    _children = ['head', 'content', 'foot', 'caption']

    def __init__(self, *args, head=None, foot=None, caption=None,
                 colspec=None, identifier='', classes=[], attributes={}):

        self._set_ica(identifier, classes, attributes)
        self._set_content(args, TableBody)
        self.caption = caption

        self._set_table_width()  # also fills in colspec if it's empty
        self.head = head
        self.foot = foot
        # Colspec is a list of (alignment, width) tuples
        # TODO: add validation to colspec
        self.colspec = [(check_group(a, TABLE_ALIGNMENT),
                         check_type_or_value(w, (float, int), 'ColWidthDefault'))
                        for (a, w) in colspec] if colspec else [('AlignDefault', 'ColWidthDefault')] * self.cols
        self._validate_colspec()

    def _set_table_width(self):
        self.cols = 0
        if self.content and self.content[0].content:
            self.cols = count_columns_in_row(self.content[0].content[0].content)  # Table -> First TableBody -> IntermediateBody -> First Row

    def _validate_cols(self, block):
        if not len(block.content):
            return

        block_cols = count_columns_in_row(block.content[0].content)

        if not self.cols:
            self.cols = block_cols
        elif self.cols != block_cols:
            msg = f'\n\nInvalid number of columns in table {block.location}.'
            msg += f'Expected {self.cols} but received {block_cols}\n'
            raise IndexError(msg)

    def _validate_colspec(self):
        if self.cols != len(self.colspec):
            msg = '\n\nInvalid number of colspec tuples.'
            msg += 'Expected {} but received {}\n'.format(self.cols, len(self.colspec))
            raise IndexError(msg)

    @property
    def head(self):
        return self._head

    @head.setter
    def head(self, value):
        self._head = check_type(value, TableHead) if value else TableHead()
        self._head.parent = self
        self._head.location = 'head'
        self._validate_cols(self.head)

    @property
    def foot(self):
        return self._foot

    @foot.setter
    def foot(self, value):
        self._foot = check_type(value, TableFoot) if value else TableFoot()
        self._foot.parent = self
        self._foot.location = 'foot'
        self._validate_cols(self.foot)

    @property
    def caption(self):
        return self._caption

    @caption.setter
    def caption(self, value):
        self._caption = check_type_or_value(value, Caption, None)
        if self._caption is not None:
            self._caption.parent = self
            self._caption.location = 'caption'

    def _slots_to_json(self):
        ica = self._ica_to_json()
        caption = self.caption.to_json()
        colspec = [[{'t': a}, colspec_to_json(c)] for a, c in self.colspec]
        head = self.head.to_json()
        bodies = [body._slots_to_json() for body in self.content]
        foot = self.foot.to_json()
        return [ica, caption, colspec, head, bodies, foot]


class TableHead(Block):
    """
    The head of a table, containing a one or more head rows, plus optional attributes

    :param row: head rows
    :type row: :class:`str`
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
        self._set_content(args, TableRow)

    def to_json(self):
        return [self._ica_to_json(), self.content.to_json()]


class TableFoot(Block):
    """
    The foot of a table, containing a one or more foot rows, plus optional attributes

    :param row: foot rows
    :type row: :class:`str`
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
        self._set_content(args, TableRow)

    def to_json(self):
        return [self._ica_to_json(), self.content.to_json()]


class TableBody(Block):
    """
    Body of a table, containing a list of intermediate head rows, a list of table body rows, row_head_columns, plus optional attributes

    :param row: head rows
    :type row: :class:`str`
    :param head: Intermediate head (list of table rows)
    :type head: :class:`list` of :class:`TableRow`
    :param row_head_columns: number of columns on the left that are considered column headers (default: 0)
    :type row_head_columns: class:`int`
    :param identifier: element identifier (usually unique)
    :type identifier: :class:`str`
    :param classes: class names of the element
    :type classes: :class:`list` of :class:`str`
    :param attributes: additional attributes
    :type attributes: :class:`dict`
    :Base: :class:`Block`
     """

    __slots__ = ['_content', '_head', 'row_head_columns', 'identifier', 'classes', 'attributes']
    _children = ['content', 'head']

    def __init__(self, *args, head=None, row_head_columns=0,
                 identifier='', classes=[], attributes={}):
        self._set_ica(identifier, classes, attributes)
        self._set_content(args, TableRow)
        self.head = head
        self.row_head_columns = check_type(row_head_columns, int)

    @property
    def head(self):
        return self._head

    @head.setter
    def head(self, value):
        if value:
            value = value.list if isinstance(value, ListContainer) else list(value)
        else:
            value = []
        self._head = ListContainer(*value, oktypes=TableRow, parent=self)
        self._head.location = 'head'

    def _slots_to_json(self):
        return [self._ica_to_json(), self.row_head_columns,
                self.head.to_json(), self.content.to_json()]


class TableRow(Element):
    """
    Table Row

    :param args: cells
    :type args: :class:`TableCell`
    :param identifier: element identifier (usually unique)
    :type identifier: :class:`str`
    :param classes: class names of the element
    :type classes: :class:`list` of :class:`str`
    :param attributes: additional attributes
    :type attributes: :class:`dict`
    :Base: :class:`Element`
     """
    __slots__ = ['_content', 'identifier', 'classes', 'attributes']
    _children = ['content']

    def __init__(self, *args, identifier='', classes=[], attributes={}):
        self._set_ica(identifier, classes, attributes)
        self._set_content(args, TableCell)

    def to_json(self):
        return [self._ica_to_json(), self.content.to_json()]


class TableCell(Element):
    """
    Table Cell

    :param args: elements
    :type args: :class:`Block`
    :param alignment: row alignment
        (either 'AlignLeft', 'AlignRight', 'AlignCenter' or 'AlignDefault').
    :type alignment: :class:`str`
    :param rowspan: number of rows occupied by a cell (height of a cell)
    :type rowspan: :class:`int`
    :param colspan: number of columns occupied by a cell (width of a cell)
    :type colspan: :class:`int`
    :param identifier: element identifier (usually unique)
    :type identifier: :class:`str`
    :param classes: class names of the element
    :type classes: :class:`list` of :class:`str`
    :param attributes: additional attributes
    :type attributes: :class:`dict`
    :Base: :class:`Element`
     """
    __slots__ = ['_content', 'alignment', 'rowspan', 'colspan',
                 'identifier', 'classes', 'attributes']
    _children = ['content']

    def __init__(self, *args, alignment='AlignDefault', rowspan=1, colspan=1,
                 identifier='', classes=[], attributes={}):

        self._set_ica(identifier, classes, attributes)
        self._set_content(args, Block)
        self.alignment = check_group(alignment, TABLE_ALIGNMENT)
        self.rowspan = rowspan
        self.colspan = colspan
        if (self.rowspan <= 0):
            raise TypeError('Cell rowspan must be positive')
        if (self.colspan <= 0):
            raise TypeError('Cell colspan must be positive')

    def to_json(self):
        return [self._ica_to_json(), {'t': self.alignment}, self.rowspan,
                self.colspan, self.content.to_json()]


class Caption(Element):
    """
    Table caption with optional short caption

    :param args: caption
    :type args: :class:`Block`
    :param short_caption: Short caption
    :type short_caption: :class:`list` of :class:`Inline`
    :param identifier: element identifier (usually unique)
    :Base: :class:`Element`
     """

    __slots__ = ['_content', '_short_caption']
    _children = ['content', 'short_caption']

    def __init__(self, *args, short_caption=None):
        self._set_content(args, Block)
        self.short_caption = short_caption

    def to_json(self):
        short_caption = None if self.short_caption is None else self.short_caption.to_json()
        return [short_caption, self.content.to_json()]

    @property
    def short_caption(self):
        return self._short_caption

    @short_caption.setter
    def short_caption(self, value):
        if value:
            value = value.list if isinstance(value, ListContainer) else list(value)
            self._short_caption = ListContainer(*value, oktypes=Inline, parent=self)
            self._short_caption.location = 'short_caption'
        else:
            self._short_caption = None


# ---------------------------
# Constants
# ---------------------------

TABLE_ALIGNMENT = {'AlignLeft', 'AlignRight', 'AlignCenter', 'AlignDefault'}
TABLE_WIDTH = {'ColWidthDefault'}


# ---------------------------
# Functions
# ---------------------------

def count_columns_in_row(row):
    return sum(cell.colspan for cell in row)


def colspec_to_json(c):
    return {'t': c} if c == 'ColWidthDefault' else encode_dict('ColWidth', c)


def cell_from_json(c):
    return TableCell(*c[4], alignment=c[1], rowspan=c[2], colspan=c[3],
                     **decode_ica(c[0]))


def row_from_json(c):
    return TableRow(*map(cell_from_json, c[1]), **decode_ica(c[0]))


def body_from_json(c):
    row_head_columns = c[1]
    head = map(row_from_json, c[2])
    body = map(row_from_json, c[3])
    return TableBody(*body, head=head, row_head_columns=row_head_columns,
                     **decode_ica(c[0]))


def table_from_json(c):
    # Attr Caption [ColSpec] TableHead [TableBody] TableFoot
    ica = decode_ica(c[0])
    caption = Caption(*c[1][1], short_caption=c[1][0])
    colspec = c[2]
    head = TableHead(*map(row_from_json, c[3][1]), **decode_ica(c[3][0]))
    bodies = map(body_from_json, c[4])
    foot = TableFoot(*map(row_from_json, c[5][1]), **decode_ica(c[5][0]))
    return Table(*bodies, head=head, foot=foot, caption=caption, colspec=colspec, **ica)
