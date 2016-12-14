"""
Panflute filter to allow file includes

Each include statement has its own line and has the syntax:

    $include ../somefolder/somefile

Each include statement must be in its own paragraph. That is, in its own line
and separated by blank lines.

If no extension was given, ".md" is assumed.
"""

import os
import panflute as pf


def is_include_line(elem):
    if len(elem.content) < 3:
        return False
    elif not all (isinstance(x, (pf.Str, pf.Space)) for x in elem.content):
        return False
    elif elem.content[0].text != '$include':
        return False
    elif type(elem.content[1]) != pf.Space:
        return False
    else:
        return True


def get_filename(elem):
    fn = pf.stringify(elem, newlines=False).split(maxsplit=1)[1]
    if not os.path.splitext(fn)[1]:
        fn += '.md'
    return fn


def action(elem, doc):
    if isinstance(elem, pf.Para) and is_include_line(elem):
        
        fn = get_filename(elem)
        if not os.path.isfile(fn):
            return
        
        with open(fn) as f:
            raw = f.read()

        new_elems = pf.convert_text(raw)
        
        # Alternative A:
        return new_elems
        # Alternative B:
        # div = pf.Div(*new_elems, attributes={'source': fn})
        # return div


def main(doc=None):
    return pf.run_filter(action, doc=doc) 


if __name__ == '__main__':
    main()
