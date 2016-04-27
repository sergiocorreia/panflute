"""
Serialize JSON dump into AST and vice versa

For the Pandoc element definitions, see:
- Readable format:
  https://hackage.haskell.org/package/pandoc-types-1.16.1/docs/Text-Pandoc-Definition.html
- Recent updates:
  https://github.com/jgm/pandoc-types/commits/master/Text/Pandoc/Definition.hs

"""
# ---------------------------
# Imports
# ---------------------------

from .elements import Element, Doc, from_json, to_json
from .elements import Space, LineBreak, SoftBreak, Para

import io
import sys
import json
import codecs  # Used in sys.stdout writer
from collections import OrderedDict
from functools import partial


# ---------------------------
# Constants
# ---------------------------

Spaces = (Space, LineBreak, SoftBreak)

VerticalSpaces = (Para, )


# ---------------------------
# Functions
# ---------------------------

def load(input_stream=None):
    """Load JSON-encoded document and return Doc class

    If no input stream is set (a file handle), will load from stdin"""

    if input_stream is None:
        input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

    # Load JSON and validate it
    doc = json.load(input_stream, object_pairs_hook=from_json)
    assert len(doc) == 2, 'json.load returned list with unexpected size:'
    metadata, items = doc
    assert type(items) == list

    # Output format
    format = sys.argv[1] if len(sys.argv) > 1 else 'html'

    doc = Doc(metadata=metadata, items=items, format=format)
    
    # Augment doc with an open Pandoc process
    return doc


def dump(doc, output_stream=None):
    """
    ...
    """

    assert type(doc) == Doc
    if output_stream is None:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        output_stream = sys.stdout

    json.dump(
        obj=doc,
        fp=output_stream,
        default=to_json,  # Serializer
        separators=(',', ':'),  # Compact separators, like Pandoc
        ensure_ascii=False  # For Pandoc compat
    )


def is_container(element):
    return isinstance(element, (list, tuple, Element))


def get_containers(element):
    assert isinstance(element, Element)
    items = (getattr(element, slot) for slot in element.__slots__)
    items = [item for item in items if is_container(item)]
    return items


def walk(element, action, doc):
    """Walk through every Pandoc element and apply action(element, doc)

    The doc class contains the .metadata and .format attributes, as well as
    any optional attributes (such as backmatter) which gives it
    flexibility."""

    # Use this when debugging, to bypass pandoc (which intercepts stdout)
    # print("WARNING: ", element, file=sys.stderr)

    assert element is doc or is_container(element), type(element)

    # element can be doc, a normal element, or a list

    if element is doc:
        doc.items = walk(doc.items, action, doc)
        # TODO: Walk metadata?
        return doc
    elif isinstance(element, Element):
        # Apply filter to the element
        altered = action(element, doc)
        # Returning [] is the same as deleting the element (pandocfilters.py)
        if altered == []:
            return []
        # Returning None is the same as keeping it unchanged (pandocfilters.py)
        elif altered is None:
            altered = element
        for item in get_containers(altered):
            item = walk(item, action, doc)
    else:
        altered = []
        for item in element:
            if isinstance(item, Element):
                item = walk(item, action, doc)
                # Returning [] will drop the item if it was an Element
                if item != []:
                    altered.append(item)
            elif isinstance(item, (list, tuple)):
                item = walk(item, action, doc)
                altered.append(item)
            else:
                altered.append(item)
    # Remove this: assert that ans is not empty if input was not empty
    if element:
        assert altered != []
    return altered


def toJSONFilters(actions,
                  prepare=None, finalize=None,
                  input_stream=None, output_stream=None,
                  **kwargs):
    """
    ...
    """
    doc = load(input_stream=input_stream)
    if prepare is not None:
        prepare(doc)
    for action in actions:
        if kwargs:
            action = partial(action, **kwargs)
        doc.items = walk(doc.items, action, doc)
    if finalize is not None:
        finalize(doc)
    dump(doc, output_stream=output_stream)


def toJSONFilter(action, *args, **kwargs):
    """
    ...
    """
    return toJSONFilters([action], *args, **kwargs)

# ---------------------------
# Useful Functions
# ---------------------------

def stringify(element):
    """
    ...
    """
    assert is_container(element)
    ans = []

    if isinstance(element, Element):
        if hasattr(element, 'text'):
            ans.append(element.text)
        for item in get_containers(element):
            ans.append(stringify(item))
        if isinstance(element, Spaces):
            ans.append(' ')
        if isinstance(element, VerticalSpaces):
            ans.append('\n\n')
    else:
        for item in element:
            ans.append(stringify(item) if is_container(item) else str(item))
    return ''.join(ans)
