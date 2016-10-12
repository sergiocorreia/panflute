#!/usr/bin/env python

"""
Pandoc filter that causes emphasized text to be displayed
in ALL CAPS.
"""

from panflute import toJSONFilter, Emph, Str
from caps import caps


def deemph(elem, doc):
    if type(elem) == Emph:
        # Make Str elements in Emph uppercase
        elem.walk(caps)

        # Append them to Emph's parent (after the emph)
        for i, item in enumerate(elem.content, elem.index + 1):
            elem.parent.content.insert(i, item)

        # Delete the emph
        return []


if __name__ == "__main__":
    toJSONFilter(deemph)
