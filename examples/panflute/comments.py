#!/usr/bin/env python
import panflute as pf
import re

"""
Pandoc filter that causes everything between
'<!-- BEGIN COMMENT -->' and '<!-- END COMMENT -->'
to be ignored.  The comment lines must appear on
lines by themselves, with blank lines surrounding
them.
"""


def prepare(doc):
    doc.ignore = False


def comment(el, doc):
    is_relevant = (type(el) == pf.RawBlock) and (doc.format == 'html')
    if is_relevant and re.search("<!-- BEGIN COMMENT -->", el.text):
        doc.ignore = True
    if doc.ignore:
        if is_relevant and re.search("<!-- END COMMENT -->", el.text):
            doc.ignore = False
        return []

if __name__ == "__main__":
    pf.toJSONFilter(comment, prepare=prepare)
