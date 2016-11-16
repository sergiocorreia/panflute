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


def main(doc=None):
    return run_filter(action, prepare, finalize, doc=doc)


if __name__ == '__main__':
    main()
