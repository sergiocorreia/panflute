"""
Move tables to where the string $tables is.
"""

from panflute import *

def prepare(doc):
    doc.backmatter = []

def action(elem, doc):
    if isinstance(elem, Table):
        doc.backmatter.append(elem)
        return []

def finalize(doc):
    div = Div(*doc.backmatter)
    doc = doc.replace_keyword('$tables', div)

if __name__ == '__main__':
    toJSONFilter(action, prepare, finalize)
