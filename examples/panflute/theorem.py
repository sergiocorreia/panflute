#!/usr/bin/env python

"""
Pandoc filter to convert divs with class="theorem" to LaTeX
theorem environments in LaTeX output, and to numbered theorems
in HTML output.
"""

from panflute import Div, RawBlock, toJSONFilter

def prepare(doc):
    doc.theoremcount = 0

def theorems(e, doc):
    if type(e) == Div and 'theorem' in e.classes:
        doc.theoremcount += 1
        if doc.format == 'latex':
            label = '\\label{' + e.identifier + '}' if e.identifier else ''
            left = RawBlock('\\begin{theorem}' + label, format='latex')
            right = RawBlock('\\end{theorem}', format='latex')
        elif doc.format in ('html', 'html5'):
            label = '<dt>Theorem {}</dt>\n<dd>'.format(doc.theoremcount)
            left = RawBlock(label, format='html')
            right = RawBlock('</dd>\n</dl>', format='html')
        else:
            return

        e.content = [left] + list(e.content) + [right]
        return e


if __name__ == "__main__":
    toJSONFilter(theorems, prepare=prepare)
