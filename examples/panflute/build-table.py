from panflute import *


def add_table_without_header(options, data, element, doc):
    cells = ['', 'Quality', 'Age', 'Sex', 'Memo']
    cells = [TableCell(Plain(Str(cell))) for cell in cells]
    row = TableRow(*cells)
    
    body = TableBody(row)

    width = [0.16, 0.16, 0.16, 0.16, 0.16]
    alignment = ['AlignDefault'] * len(width)
    caption = 'This table should not have a header'
    caption = Caption(Para(Str(caption)))
    return Div(Table(body, colspec=zip(alignment, width), caption=caption))


def add_table_with_only_header(options, data, element, doc):
    cells = ['', 'Quality', 'Age', 'Sex', 'Memo']
    cells = [TableCell(Plain(Str(cell))) for cell in cells]
    row = TableRow(*cells)
    head = TableHead(row)
    width = [0.16, 0.16, 0.16, 0.16, 0.16]
    alignment = ['AlignDefault'] * len(width)
    caption = 'This table should only have a header; and no rows'
    caption = Caption(Plain(Str(caption)))
    return Div(Table(head=head, colspec=zip(alignment, width), caption=caption))


def finalize(doc):
    doc.walk(view_table_info, doc=doc)


def view_table_info(e, doc):
    if isinstance(e, Table):
        debug('[TABLE]')
        debug('Cols:  ', e.cols)
        debug('Head :', e.head is not None)
        debug('Foot :', e.foot is not None)
        debug('Caption:', stringify(e.caption))
        debug()


def main(doc=None):
    d = {'table_without_header': add_table_without_header,
         'table_only_header': add_table_with_only_header}
    return run_filter(yaml_filter, tags=d, doc=doc, finalize=finalize)


if __name__ == '__main__':
  main()
