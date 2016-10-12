from panflute import *

def add_one(e, doc):
    if type(e) == TableCell and stringify(e).isdigit():
        chunk = cell.content[0].content[0]
        chunk.text = str(int(chunk.text) + 1)


def idea(e, doc):
    selector = 'Table Items Rows Cells'

    if any(type(a)==pf.Table for a in e.ancestors()):
        pass


if __name__ == '__main__':
    pf.toJSONFilter(add_one)