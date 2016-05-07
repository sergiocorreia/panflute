"""
Pandoc filter using panflute
"""

import panflute as pf


def prepare(doc):
    pass


def action(elem, doc):
    if isinstance(elem, pf.Element) and doc.format == 'latex':
        pass
        # return None -> element unchanged
        # return [] -> delete element


def finalize(doc):
    pass


if __name__ == '__main__':
    pf.toJSONFilter(action, prepare=prepare, finalize=finalize)
