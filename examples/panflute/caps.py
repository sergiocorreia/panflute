#!/usr/bin/env python

"""
Pandoc filter to convert all regular text to uppercase.
Code, link URLs, etc. are not affected.
"""

from panflute import run_filter, Str


def caps(elem, doc):
    if type(elem) == Str:
        elem.text = elem.text.upper()
        return elem


def main(doc=None):
    return run_filter(caps, doc=doc)


if __name__ == "__main__":
    main()
