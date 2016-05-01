"""
Panflute: pandoc filters made simple
====================================

Panflute is a Python package that makes `Pandoc <http://pandoc.org/>`_ filters easier to write.

It is a pythonic alternative to John MacFarlane's
`pandocfilters <https://github.com/jgm/pandocfilters>`_,
from which it is heavily inspired.

To use it, write a function that works on Pandoc elements
and call it through `toJSONFilter <code.html#panflute.io.toJSONFilter>`_::

    from panflute import *
    
    def increase_header_level(elem, doc):
        if type(elem)==Header:
            if elem.level < 6:
                elem.level += 1
            else:
                return [] #  Delete headers already in level 6
    
    if __name__ == "__main__":
        toJSONFilter(increase_header_level)


Motivation
====================================

Panflute aims to replace pandocfilters with a pythonic alternative that
comes with batteries included, to help with some of the most common tasks.

It's Pythonic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Elements are easier to modify. For instance, to change the level of a header, you can do ``header.level += 1`` instead of ``header['c'][0] += 1``. To change the identifier, do ``header.identifier = 'spam'`` instead of ``header['c'][1][1] = 'spam'``
- Elements are easier to create. Thus, to create a header you can do ``Header(Str(The), Space, Str(Title), level=1, identifier=foo)``
  instead of ``Header([1,["foo",[],[]],[{"t":"Str","c":"The"},{"t":"Space","c":[]},{"t":"Str","c":"Title"}])``

Detects common mistakes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Check that the elements contain the correct types. Trying to create `Para('text')` will give you the error "Para() element must contain Inlines but received a str()", instead of just failing silently when running the filter.

Comes with batteries included:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Convert markdown strings into python objects or other formats, with the `convert_markdown(text, format)` function (which calls Pandoc internally)
- Use code blocks to hold YAML options and other data (such as CSV) with `yaml_filter(element, doc, tag, function)`.
- Called external programs to fetch results with `shell()`.
- Modifying the entire document (e.g. moving all the figures and tables to the back of a PDF) are easy to use, thanks to the `prepare` and `finalize` options of `toJSONFilter`, and to the `replace_keyword` function


More about Pandoc filters:
====================================

- For a guide to pandocfilters, see the `repository <https://github.com/jgm/pandocfilters>`_
  and the `tutorial <http://pandoc.org/scripting.html>`_.
- The repo includes `sample filters <https://github.com/jgm/pandocfilters/tree/master/examples>`_.
- The wiki lists useful `third party filters <https://github.com/jgm/pandoc/wiki/Pandoc-Filters>`_.


"""

from .base import Element, Block, Inline  # , Items

from .elements import (
    Doc, Citation, TableRow, TableCell, ListItem, DefinitionItem, Definition)

from .elements import (
    Null, HorizontalRule, Space, SoftBreak, LineBreak, Str,
    Code, BlockQuote, Note, Div, Plain, Para, Emph, Strong, Strikeout,
    Superscript, Subscript, SmallCaps, Span, RawBlock, RawInline, Math,
    CodeBlock, Link, Image, BulletList, OrderedList, DefinitionList, Header,
    Quoted, Cite, Table)

# from .elements import from_json

from .io import load, dump, toJSONFilter, toJSONFilters, stringify

from .tools import yaml_filter, shell, convert_markdown, debug, replace_keyword
