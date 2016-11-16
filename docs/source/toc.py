"""
Add table of contents at the beginning;
uses optional metadata value 'toc-depth'
"""

from panflute import *

def prepare(doc):
    doc.toc = BulletList()
    doc.depth = int(doc.get_metadata('toc-depth', default=1))

def action(elem, doc):
    if isinstance(elem, Header) and elem.level <= doc.depth:
        item = ListItem(Plain(*elem.content))
        doc.toc.content.append(item)

def finalize(doc):
    doc.content.insert(0, doc.toc)
    del doc.toc, doc.depth

if __name__ == '__main__':
    run_filter(action, prepare, finalize)
