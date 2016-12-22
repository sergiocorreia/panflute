"""
Remove all tables
"""

from panflute import *


def action(elem, doc):
    if isinstance(elem, Table):
        return []


def main(doc=None):
    return run_filter(action, doc=doc)


if __name__ == '__main__':
    main()
