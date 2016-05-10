#!/usr/bin/env python

"""
Pandoc filter to convert all regular text to uppercase.
Code, link URLs, etc. are not affected.
"""

from panflute import toJSONFilter, Str


def caps(elem, doc):
    if type(elem) == Str:
        elem.text = elem.text.upper()
        return elem


if __name__ == "__main__":
    toJSONFilter(caps)