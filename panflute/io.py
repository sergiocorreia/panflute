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
from collections import OrderedDict
from functools import partial

py2 = sys.version_info[0] == 2


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
        input_stream = io.open(sys.stdin.fileno()) if py2 else io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

    # Load JSON and validate it
    doc = json.load(input_stream, object_pairs_hook=from_json)

    # Notes:
    # - We use 'object_pairs_hook' instead of 'object_hook' to preserve the
    #   order of the metadata.
    # - The hook gets called for dicts (not lists), and the deepest dicts
    #   get called first (so you can ensure that when you receive a dict,
    #   its contents have already been fed to the hook).

    # Compatibility:
    # - Before Pandoc 1.8 (1.7 or earlier, AKA "Pandoc Legacy"),
    #   the JSON is a list:
    #   [{"unMeta":{META}},[BLOCKS]]
    # - Afterwards, it's a dict:
    #   {"pandoc-api-version" : [MAJ, MIN, REV],
    #    "meta" : META, "blocks": BLOCKS}
    # - This means that on legacy, the hook WILL NOT get called on the entire
    #   document and we need to create the Doc() element by hand

    # Corner cases:
    # - If META is missing, 'object_pairs_hook' will receive an empty list

    # Output format
    format = sys.argv[1] if len(sys.argv) > 1 else 'html'

    # API Version
    if isinstance(doc, Doc):
        # Modern Pandoc
        doc.format = format
        pass
    else:
        # Legacy Pandoc
        metadata, items = doc
        assert type(items) == list
        assert len(doc) == 2, 'json.load returned list with unexpected size:'
        doc = Doc(*items, metadata=metadata, format=format)

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

    assert type(doc) == Doc, "panflute.dump needs input of type panflute.Doc"
    if output_stream is None:
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout) if py2 else codecs.getwriter("utf-8")(sys.stdout.detach())
        output_stream = sys.stdout

    # Switch to legacy JSON output; eg: {'t': 'Space', 'c': []}
    if doc.api_version is None:

        # Switch .to_json() to legacy
        Citation.backup = Citation.to_json
        Citation.to_json = Citation.to_json_legacy

        # Switch ._slots_to_json() to legacy
        for E in [Table, OrderedList, Quoted, Math]:
            E.backup = E._slots_to_json
            E._slots_to_json = E._slots_to_json_legacy

        # Switch .to_json() to method of base class
        for E in EMPTY_ELEMENTS:
            E.backup = E.to_json
            E.to_json = Element.to_json

    json_serializer = lambda elem: elem.to_json()

    output_stream.write(json.dumps(
        obj=doc,
        default=json_serializer,  # Serializer
        check_circular=False,
        separators=(',', ':'),  # Compact separators, like Pandoc
        ensure_ascii=False  # For Pandoc compat
    ))

    # Undo legacy changes
    if doc.api_version is None:
        Citation.to_json = Citation.backup
        for E in [Table, OrderedList, Quoted, Math]:
            E._slots_to_json = E.backup
        for E in EMPTY_ELEMENTS:
            E.to_json = E.backup


def toJSONFilters(*args, **kwargs):
    """
    Wrapper for :func:`.run_filters`
    """
    return run_filters(*args, **kwargs)


def toJSONFilter(*args, **kwargs):
    """
    Wapper for :func:`.run_filter`, which calls :func:`.run_filters`

    toJSONFilter(action, prepare=None, finalize=None, input_stream=None, output_stream=None, \*\*kwargs)
    Receive a Pandoc document from stdin, apply the *action* function to each element, and write it back to stdout.

    See also :func:`.toJSONFilters`
    """
    return run_filter(*args, **kwargs)


def run_filters(actions,
                prepare=None, finalize=None,
                input_stream=None, output_stream=None,
                doc=None,
                **kwargs):
    """
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
        doc = doc.walk(action, doc)

    if finalize is not None:
        finalize(doc)

    if load_and_dump:
        dump(doc, output_stream=output_stream)
    else:
        return(doc)


def run_filter(action, *args, **kwargs):
    """
     Wapper for :func:`.run_filters`

    Receive a Pandoc document from stdin, apply the *action* function to each element, and write it back to stdout.

    See :func:`.run_filters`
    """
    return run_filters([action], *args, **kwargs)


def load_reader_options():
    """
    Retrieve Pandoc Reader options from the environment
    """
    options = os.environ['PANDOC_READER_OPTIONS']
    options = json.loads(options, object_pairs_hook=OrderedDict)
    return options
