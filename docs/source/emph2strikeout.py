"""
Replace Emph elements with Strikeout elements
"""

from panflute import *


def action(elem, doc):
    if isinstance(elem, Emph):
        return Strikeout(*elem.content)


def main(doc=None):
    return run_filter(action, doc=doc)


if __name__ == '__main__':
    main()
