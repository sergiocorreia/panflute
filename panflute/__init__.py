"""
Panflute: pandoc filters made simple
====================================

Panflute is a Python package that makes `Pandoc <http://pandoc.org/>`_
filters fun to write. (`Installation <install.html>`_)
"""

from .containers import ListContainer, DictContainer

from .base import Element, Block, Inline, MetaValue

# These elements are not part of pandoc-types
from .elements import (
    Doc, Citation, TableRow, TableCell, ListItem,
    DefinitionItem, Definition, LineItem)

from .elements import (
    Null, HorizontalRule, Space, SoftBreak, LineBreak, Str,
    Code, BlockQuote, Note, Div, Plain, Para, Emph, Strong, Strikeout,
    Superscript, Subscript, SmallCaps, Span, RawBlock, RawInline, Math,
    CodeBlock, Link, Image, BulletList, OrderedList, DefinitionList,
    LineBlock, Header, Quoted, Cite, Table)

from .elements import (
    MetaList, MetaMap, MetaString, MetaBool, MetaInlines, MetaBlocks)

from .io import load, dump, run_filter, run_filters
from .io import toJSONFilter, toJSONFilters  # Wrappers
from .io import load_reader_options

from .tools import (
    stringify, yaml_filter, shell, run_pandoc, convert_text, debug, get_option)

from .autofilter import main

from .version import __version__
