"""
Make text in the last row of every table bold
"""

import panflute as pf


def action(elem, doc):
    if isinstance(elem, pf.TableRow):
        # Exclude table headers (which are not in a list)
        if elem.index is None:
            return

        if elem.next is None:
            pf.debug(elem)
            elem.walk(make_emph)


def make_emph(elem, doc):
    if isinstance(elem, pf.Str):
        return pf.Emph(elem)


def main(doc=None):
    return pf.run_filter(action, doc=doc) 


if __name__ == '__main__':
    main()
