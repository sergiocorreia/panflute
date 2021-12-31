"""
I/O related functions
"""


# ---------------------------
# Imports
# ---------------------------

from .elements import Element, Doc, from_json, ListContainer

# These will get modified if using Pandoc legacy (<1.8)
from .elements import (Citation, Table, OrderedList, Quoted,
                       Math, EMPTY_ELEMENTS)

import io
import os
import sys
import json
import codecs  # Used in sys.stdout writer
from functools import partial


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
        >>> raw = '[{"unMeta":{}},
        [{"t":"Para","c":[{"t":"Str","c":"Hello!"}]}]]'
        >>> f = io.StringIO(raw)
        >>> doc = pf.load(f)

    :param input_stream: text stream used as input
        (default is :data:`sys.stdin`)
    :rtype: :class:`.Doc`
    """

    if input_stream is None:
        input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

    # Load JSON and validate it
    doc = json.load(input_stream, object_hook=from_json)

    # Notes:
    # - The hook gets called for dicts (not lists), and the deepest dicts
    #   get called first (so you can ensure that when you receive a dict,
    #   its contents have already been fed to the hook).

    # Compatibility:
    # - As of Pandoc 1.9, JSON input is a dict:
    #   {"pandoc-api-version" : [MAJ, MIN, REV],
    #    "meta" : META, "blocks": BLOCKS}

    # Corner cases:
    # - If META is missing, 'object_hook' will receive an empty list

    # Output format
    format = sys.argv[1] if len(sys.argv) > 1 else 'html'

    # API Version
    assert isinstance(doc, Doc)
    doc.format = format
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

        >>> with open('some-document.json', 'w', encoding='utf-8') as f:
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

    if not isinstance(doc, Doc):
        msg = f'panflute.dump needs input of type "panflute.Doc" but received one of type "{type(doc).__name__}"'
        raise TypeError(msg)

    if output_stream is None:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        output_stream = sys.stdout

    json_serializer = lambda elem: elem.to_json()

    output_stream.write(json.dumps(
        obj=doc,
        default=json_serializer,  # Serializer
        check_circular=False,
        separators=(',', ':'),  # Compact separators, like Pandoc
        ensure_ascii=False  # For Pandoc compat
    ))


def toJSONFilters(*args, **kwargs):
    """
    Wrapper for :func:`.run_filters`
    """
    return run_filters(*args, **kwargs)


def toJSONFilter(*args, **kwargs):
    """
    Wrapper for :func:`.run_filter`, which calls :func:`.run_filters`

    toJSONFilter(action, prepare=None, finalize=None, input_stream=None, output_stream=None, \*\*kwargs)
    Receive a Pandoc document from stdin, apply the *action* function to each element, and write it back to stdout.

    See also :func:`.toJSONFilters`
    """
    return run_filter(*args, **kwargs)


def run_filters(actions,
                prepare=None, finalize=None,
                input_stream=None, output_stream=None,
                doc=None,
                walk_inlines=True,
                **kwargs):
    r"""
    Receive a Pandoc document from the input stream (default is stdin),
    walk through it applying the functions in *actions* to each element,
    and write it back to the output stream (default is stdout).

    Notes:

    - It receives and writes the Pandoc documents as JSON--encoded strings;
      this is done through the :func:`.load` and :func:`.dump` functions.
    - It walks through the document once for every function in *actions*,
      so the actions are applied sequentially.
    - By default, it will read from stdin and write to stdout,
      but these can be modified.
    - It can also apply functions to the entire document at the beginning and
      end; this allows for global operations on the document.
    - If ``doc`` is a :class:`.Doc` instead of ``None``, ``run_filters``
      will return the document instead of writing it to the output stream.

    :param actions: sequence of functions; each function takes (element, doc)
     as argument, so a valid header would be ``def action(elem, doc):``
    :type actions: [:class:`function`]
    :param prepare: function executed at the beginning;
     right after the document is received and parsed
    :type prepare: :class:`function`
    :param finalize: function executed at the end;
     right before the document is converted back to JSON and written to stdout.
    :type finalize: :class:`function`
    :param input_stream: text stream used as input
        (default is :data:`sys.stdin`)
    :param output_stream: text stream used as output
        (default is :data:`sys.stdout`)
    :param doc: ``None`` unless running panflute as a filter, in which case this will be a :class:`.Doc` element
    :type doc: ``None`` | :class:`.Doc`
    :param \*kwargs: keyword arguments will be passed through to the *action*
     functions (so they can actually receive more than just two arguments
     (*element* and *doc*)
    """

    load_and_dump = (doc is None)

    if load_and_dump:
        doc = load(input_stream=input_stream)

    if prepare is not None:
        prepare(doc)

    for action in actions:
        if kwargs:
            action = partial(action, **kwargs)
        doc = doc.walk(action, doc=doc, walk_inlines=walk_inlines)

    if finalize is not None:
        finalize(doc)

    if load_and_dump:
        dump(doc, output_stream=output_stream)
    else:
        return(doc)


def run_filter(action, *args, **kwargs):
    """
    Wrapper for :func:`.run_filters`

    Receive a Pandoc document from stdin, apply the *action* function to each element, and write it back to stdout.

    See :func:`.run_filters`
    """
    return run_filters([action], *args, **kwargs)
