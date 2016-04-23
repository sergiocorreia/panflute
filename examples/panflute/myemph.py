#!/usr/bin/env python
import panflute as pf

"""
Pandoc filter that causes emphasis to be rendered using
the custom macro '\myemph{...}' rather than '\emph{...}'
in latex.  Other output formats are unaffected.
"""


def latex(s):
    return pf.RawInline(s, format='latex')


def myemph(e, doc):
	if type(e)==pf.Emph and doc.format=='latex':
		return pf.Span(latex('\\myemph{'), *e.items, latex('}'))


if __name__ == "__main__":
    pf.toJSONFilter(myemph)
