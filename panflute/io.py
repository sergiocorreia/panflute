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

import io
import sys
import json

from .elements import from_json, to_json, Doc, Metadata


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
    assert type(metadata) == Metadata
    assert type(items) == list

    # Output format
    format = sys.argv[1] if len(sys.argv) > 1 else ""

    return Doc(metadata=metadata, items=items, format=format)


def dump(doc, output_stream=None):
    assert type(doc) == Doc
    if output_stream is None:
        output_stream = sys.stdout
    # print(output_stream) # BUGBUG Use a diff encoding?

    json.dump(
        obj=doc,
        fp=output_stream,
        default=to_json,  # Serializer
        separators=(',', ':'),  # Compact separators, like Pandoc
        ensure_ascii=False  # For Pandoc compat
    )
