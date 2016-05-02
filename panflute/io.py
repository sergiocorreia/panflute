"""
Serialize JSON dump into an element tree and vice versa
"""

# ---------------------------
# Imports
# ---------------------------

from .elements import Element, Doc, from_json, Items
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
    """
    Load JSON-encoded document and return a :class:`.Doc` element.

    The JSON input will be read from :data:`sys.stdin` unless an alternative 
    text stream is given (a file handle).

    To load from a file, you can do:

        >>> import panflute as pf
        >>> with open('some-document.json', encoding='utf-8') as f:
        >>>     doc = pf.load(f)

    To load from a string, you can do:

        >>> import io
        >>> raw = '[{"unMeta":{}},[{"t":"Para","c":[{"t":"Str","c":"Hello!"}]}]]'
        >>> f = io.StringIO(raw)
        >>> doc = pf.load(f)

    :param input_stream: text stream used as input
        (default is :data:`sys.stdin`)
    :rtype: :class:`.Doc`
    """

    if input_stream is None:
        input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

    # Load JSON and validate it
    doc = json.load(input_stream, object_pairs_hook=from_json)
    assert len(doc) == 2, 'json.load returned list with unexpected size:'
    metadata, items = doc
    assert type(items) == list

    # Output format
    format = sys.argv[1] if len(sys.argv) > 1 else 'html'

    doc = Doc(*items, metadata=metadata, format=format)
    
    # Augment doc with an open Pandoc process
    return doc


def dump(doc, output_stream=None):
    """
    Dump a :class:`.Doc` object into a JSON-encoded text string.

    The output will be sent to :data:`sys.stdout` unless an alternative 
    text stream is given.

    To dump to :data:`sys.stdout` just do:

        >>> import panflute as pf
        >>> doc = pf.Doc(Para(Str('a')))  # Create sample document
        >>> pf.dump(doc)

    To dump to file:

        >>> with open('some-document.json', 'w'. encoding='utf-8') as f:
        >>>     pf.dump(doc, f)

    To dump to a  string:

        >>> import io
        >>> with io.StringIO() as f:
        >>>     pf.dump(doc, f)
        >>>     contents = f.getvalue()

    :param doc: document, usually created with :func:`.load`
    :type doc: :class:`.Doc`
    :param output_stream: text stream used as output
        (default is :data:`sys.stdout`)
    """

    assert type(doc) == Doc
    if output_stream is None:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        output_stream = sys.stdout

    json_serializer = lambda elem: elem.to_json()

    json.dump(
        obj=doc,
        fp=output_stream,
        default=json_serializer,  # Serializer
        separators=(',', ':'),  # Compact separators, like Pandoc
        ensure_ascii=False  # For Pandoc compat
    )


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
        doc = doc.walk(action, doc)
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
