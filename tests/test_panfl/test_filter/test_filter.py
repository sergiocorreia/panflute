#!/usr/bin/env python
import sys
import panflute as pf


def action(elem, doc):
    if isinstance(elem, pf.Math):
        elem.text = elem.text.replace('-', '+') + doc.format


def main(doc=None):
    return pf.run_filter(action, doc=doc)


if __name__ == '__main__':
    main()
