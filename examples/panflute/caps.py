#!/usr/bin/env python

"""
Pandoc filter to convert all regular text to uppercase.
Code, link URLs, etc. are not affected.
"""

import panflute as pf


def caps(element, doc):
    if type(element)==pf.Str:
        element.text = element.text.upper()
        return element


if __name__ == "__main__":
    pf.toJSONFilter(caps)