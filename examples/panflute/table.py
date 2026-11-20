import panflute as pf


def rows(table):
    """All the rows of a table: head, bodies (with their intermediate heads) and foot"""
    yield from table.head.content
    for body in table.content:
        yield from body.head
        yield from body.content
    yield from table.foot.content


def add_one(e, doc):
    """Add one to every table cell that only contains a number"""
    if type(e) == pf.Table:
        for row in rows(e):
            for cell in row.content:
                if len(cell.content) == 1 and len(cell.content[0].content) == 1:
                    item = cell.content[0].content[0]
                    if isinstance(item, pf.Str) and item.text.isdigit():
                        item.text = str(int(item.text) + 1)
        return e


if __name__ == '__main__':
    pf.toJSONFilter(add_one)
