"""
Emphasize the text in the last row of every table
"""

import panflute as pf


def action(elem, doc):
    # Only the rows of a table body (not those of its head or foot,
    # nor the intermediate head rows of the body, at .location 'head')
    if (isinstance(elem, pf.TableRow) and isinstance(elem.parent, pf.TableBody)
            and elem.location is None):
        if elem.next is None:  # The last row of the body
            elem.walk(make_emph)


def make_emph(elem, doc):
    if isinstance(elem, pf.Str):
        return pf.Emph(elem)


def main(doc=None):
    return pf.run_filter(action, doc=doc) 


if __name__ == '__main__':
    main()
