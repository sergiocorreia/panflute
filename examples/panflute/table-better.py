from panflute import *


def add_one(e, doc):
    """Add one to every table cell that only contains a number"""
    if type(e) == TableCell and stringify(e).isdigit():
        chunk = e.content[0].content[0]
        chunk.text = str(int(chunk.text) + 1)


if __name__ == '__main__':
    toJSONFilter(add_one)
