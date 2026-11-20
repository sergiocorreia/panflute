"""
I/O related functions
"""


# ---------------------------
# Imports
# ---------------------------

from __future__ import annotations

from typing import TYPE_CHECKING

from .elements import Element, Doc, from_json, ListContainer

# These will get modified if using Pandoc legacy (<1.8)
from .elements import (Citation, Table, OrderedList, Quoted,
                       Math, EMPTY_ELEMENTS)

import io
import os
import sys
import json
from functools import partial

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from typing import Any
    from _typeshed import SupportsRead, SupportsWrite


# ---------------------------
# Functions
# ---------------------------

def load(input_stream: SupportsRead[str] | None = None) -> Doc:
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

    # Load JSON and validate it
    if input_stream is None:
        # Pandoc sends UTF-8, whatever the locale: read the bytes of stdin
        # (without wrapping sys.stdin.buffer in a TextIOWrapper, which would
        # close it when garbage collected)
        buffer = getattr(sys.stdin, 'buffer', None)
        if buffer is not None:
            text = buffer.read().decode('utf-8')
        else:  # sys.stdin was replaced by a text stream (e.g. io.StringIO)
            text = sys.stdin.read()
        doc = json.loads(text, object_hook=from_json)
    else:
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


def dump(doc: Doc, output_stream: SupportsWrite[str] | None = None) -> None:
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

    json_serializer = lambda elem: elem.to_json()

    text = json.dumps(
        obj=doc,
        default=json_serializer,  # Serializer
        check_circular=False,
        separators=(',', ':'),  # Compact separators, like Pandoc
        ensure_ascii=False  # For Pandoc compat
    )

    if output_stream is not None:
        output_stream.write(text)
        return

    # Pandoc expects UTF-8, whatever the locale (and the encoding of
    # sys.stdout): write the bytes to the binary buffer underneath sys.stdout
    # (without newline translation; the JSON text has no line breaks anyway)
    stdout = sys.stdout
    buffer = getattr(stdout, 'buffer', None)
    if buffer is not None:
        stdout.flush()  # Keep the order of anything written to stdout before
        buffer.write(text.encode('utf-8'))
        buffer.flush()
    else:  # sys.stdout was replaced by a text stream (e.g. io.StringIO)
        stdout.write(text)


def toJSONFilters(*args: Any, **kwargs: Any) -> Doc | None:
    """
    Wrapper for :func:`.run_filters`
    """
    return run_filters(*args, **kwargs)


def toJSONFilter(*args: Any, **kwargs: Any) -> Doc | None:
    """
    Wrapper for :func:`.run_filter`, which calls :func:`.run_filters`

    toJSONFilter(action, prepare=None, finalize=None, input_stream=None, output_stream=None, \\*\\*kwargs)
    Receive a Pandoc document from stdin, apply the *action* function to each element, and write it back to stdout.

    See also :func:`.toJSONFilters`
    """
    return run_filter(*args, **kwargs)


def run_filters(actions: Iterable[Callable[..., Element | list[Element] | None]],
                prepare: Callable[[Doc], object] | None = None,
                finalize: Callable[[Doc], object] | None = None,
                input_stream: SupportsRead[str] | None = None,
                output_stream: SupportsWrite[str] | None = None,
                doc: Doc | None = None,
                stop_if: Callable[[Element], bool] | None = None,
                **kwargs: Any) -> Doc | None:
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
    :param stop_if: function that takes (element) as argument.
    :type stop_if: :class:`function`, optional
    :param \*kwargs: keyword arguments will be passed through to the *action*
     functions (so they can actually receive more than just two arguments
     (*element* and *doc*)
    """

    load_and_dump = (doc is None)

    if load_and_dump:
        doc = load(input_stream=input_stream)

    # In what follows doc is a Doc (mypy can't infer it from load_and_dump),
    # unless an action replaced the Doc itself
    if prepare is not None:
        prepare(doc)  # type: ignore[arg-type]

    for action in actions:
        if kwargs:
            action = partial(action, **kwargs)
        doc = doc.walk(action, doc=doc, stop_if=stop_if)  # type: ignore[union-attr, assignment]

    if finalize is not None:
        finalize(doc)  # type: ignore[arg-type]

    if load_and_dump:
        dump(doc, output_stream=output_stream)  # type: ignore[arg-type]
    else:
        return(doc)


def run_filter(action: Callable[..., Element | list[Element] | None],
               *args: Any, **kwargs: Any) -> Doc | None:
    """
    Wrapper for :func:`.run_filters`

    Receive a Pandoc document from stdin, apply the *action* function to each element, and write it back to stdout.

    See :func:`.run_filters`
    """
    return run_filters([action], *args, **kwargs)
