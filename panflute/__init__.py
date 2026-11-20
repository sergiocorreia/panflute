"""
Panflute: pandoc filters made simple
====================================

Panflute is a Python package that makes `Pandoc <http://pandoc.org/>`_
filters fun to write. (`Installation <install.html>`_)
"""

# Note: the redundant "X as X" aliases mark these names as explicitly
# re-exported, for type checkers (e.g. mypy --strict, or --no-implicit-reexport)

from .utils import debug as debug

from .containers import ListContainer as ListContainer, DictContainer as DictContainer

from .base import Element as Element, Block as Block, Inline as Inline, MetaValue as MetaValue

# These elements are not part of pandoc-types
from .elements import (
    Doc as Doc, Citation as Citation, ListItem as ListItem,
    DefinitionItem as DefinitionItem, Definition as Definition, LineItem as LineItem)

from .elements import (
    Null as Null, HorizontalRule as HorizontalRule, Space as Space,
    SoftBreak as SoftBreak, LineBreak as LineBreak, Str as Str,
    Code as Code, BlockQuote as BlockQuote, Note as Note, Div as Div,
    Plain as Plain, Para as Para, Emph as Emph, Strong as Strong,
    Underline as Underline, Strikeout as Strikeout, Superscript as Superscript,
    Subscript as Subscript, SmallCaps as SmallCaps, Span as Span,
    RawBlock as RawBlock, RawInline as RawInline, Math as Math,
    CodeBlock as CodeBlock, Link as Link, Image as Image,
    BulletList as BulletList, OrderedList as OrderedList,
    DefinitionList as DefinitionList, LineBlock as LineBlock,
    Figure as Figure, Header as Header, Quoted as Quoted, Cite as Cite)

from .table_elements import (
    Table as Table, TableHead as TableHead, TableFoot as TableFoot,
    TableBody as TableBody, TableRow as TableRow, TableCell as TableCell,
    Caption as Caption)

from .elements import (
    MetaList as MetaList, MetaMap as MetaMap, MetaString as MetaString,
    MetaBool as MetaBool, MetaInlines as MetaInlines, MetaBlocks as MetaBlocks)

from .io import load as load, dump as dump, run_filter as run_filter, run_filters as run_filters
from .io import toJSONFilter as toJSONFilter, toJSONFilters as toJSONFilters  # Wrappers

from .tools import (
    stringify as stringify, yaml_filter as yaml_filter, shell as shell,
    run_pandoc as run_pandoc, convert_text as convert_text, get_option as get_option)

from .version import __version__ as __version__

# The command line interfaces in panflute.autofilter (main, panfl, stdio and
# get_filter_dirs) are imported the first time they are used, by __getattr__
# below: they need click, which takes longer to import than all of panflute.
# They are still found as attributes of this module and by dir(), and
# `from panflute import *` still imports them.
from typing import TYPE_CHECKING as _TYPE_CHECKING
if _TYPE_CHECKING:
    from .autofilter import main as main, panfl as panfl, get_filter_dirs as get_filter_dirs, stdio as stdio

# The directories in sys.path, where `panfl` looks for filters (used by
# panflute.autofilter, but computed now, as when it was imported here)
import os.path as _p
import sys as _sys
_reduced_sys_path = [d for d in _sys.path if (d not in ('', '.')) and _p.isdir(d)]

_AUTOFILTER_NAMES = ('main', 'panfl', 'get_filter_dirs', 'stdio')


def _import_autofilter():
    # (not `from . import autofilter`, which would call __getattr__('autofilter'))
    from importlib import import_module
    autofilter = import_module('panflute.autofilter')
    g = globals()
    for name in _AUTOFILTER_NAMES:
        g.setdefault(name, getattr(autofilter, name))
    return autofilter


def __getattr__(name):
    if name in _AUTOFILTER_NAMES:
        _import_autofilter()
        return globals()[name]
    if name == 'autofilter':
        return _import_autofilter()
    if name == '__all__':
        # This package has no __all__: `from panflute import *` (like pydoc
        # and others) looks for it, and when it is missing, it imports every
        # public name in the package's namespace instead. Import autofilter
        # first, so that these names include it and its functions.
        _import_autofilter()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return list(set(globals()) | set(_AUTOFILTER_NAMES) | {'autofilter'})
