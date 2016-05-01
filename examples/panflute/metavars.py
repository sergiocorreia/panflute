#!/usr/bin/env python

"""
Pandoc filter to allow interpolation of metadata fields
into a document.  %{fields} will be replaced by the field's
value.
"""

from panflute import toJSONFilter, Span, Str, MetaInlines
import re

pattern = re.compile('%\{(.*)\}$')


def metavars(elem, doc):
    if type(elem) == Str:
        m = pattern.match(elem.text)
        if m:
            field = m.group(1)
            result = doc.get_metadata(field, None)

            if type(result) == MetaInlines:
                return Span(*result.content, classes=['interpolated'],
                            attributes={'field': field})
            elif isinstance(result, str):
                return Str(result)

if __name__ == "__main__":
    toJSONFilter(metavars)
