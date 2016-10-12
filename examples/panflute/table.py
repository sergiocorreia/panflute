import panflute as pf

def add_one(e, doc):
    if type(e)==pf.Table:
        for row in e.items:
            for cell in row:
                if len(cell) == 1 and len(cell[0].items)==1:
                    text = cell[0].items[0].text
                    if text.isdigit():
                        cell[0].items[0].text = str(int(text)+1)
        return e

def idea(e, doc):
    selector = 'Table Items Rows Cells'

    if any(type(a)==pf.Table for a in e.ancestors()):
        pass

if __name__ == '__main__':
    pf.toJSONFilter(add_one)