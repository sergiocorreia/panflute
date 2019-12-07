from panflute import *


def add_table_without_header(options, data, element, doc):
    cells = ['', 'Quality', 'Age', 'Sex', 'Memo']
    cells = [TableCell(Plain(Str(cell))) for cell in cells]
    row = TableRow(*cells)
    width = [0.16, 0.16, 0.16, 0.16, 0.16]
    caption = 'This table should not have a header'
    caption = [Span(Str(caption))]
    return Div(Table(row, width=width, caption=caption))


def add_table_with_only_header(options, data, element, doc):
    cells = ['', 'Quality', 'Age', 'Sex', 'Memo']
    cells = [TableCell(Plain(Str(cell))) for cell in cells]
    row = TableRow(*cells)
    width = [0.16, 0.16, 0.16, 0.16, 0.16]
    caption = 'This table should only have a header; and no rows'
    caption = [Span(Str(caption))]
    return Div(Table(header=row, width=width, caption=caption))


def finalize(doc):
    doc.walk(view_table_info, doc=doc)


def view_table_info(e, doc):
    if isinstance(e, Table):
        debug('[TABLE]')
        debug('Rows:  ', e.rows)
        debug('Cols:  ', e.cols)
        debug('Header :', e.header is not None)
        debug('Caption:', stringify(Span(*e.caption)))
        debug()


def main(doc=None):
    d = {'table_without_header': add_table_without_header,
         'table_only_header': add_table_with_only_header}
    return run_filter(yaml_filter, tags=d, doc=doc, finalize=finalize)


if __name__ == '__main__':
  main()
