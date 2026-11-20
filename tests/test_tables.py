"""
Tests for panflute.table_elements: Table and its parts.
"""

import pytest

import panflute as pf
from panflute.table_elements import (
    cell_from_json, colspec_to_json, count_columns_in_row, table_from_json)

from .helpers import load_path, JSON_FIXTURES, roundtrip, to_json_value


def cell(text='x', **kwargs):
    return pf.TableCell(pf.Plain(pf.Str(text)), **kwargs)


def row(*texts, **kwargs):
    return pf.TableRow(*(cell(t) for t in texts), **kwargs)


def test_table_columns_inferred_from_first_body_row():
    table = pf.Table(pf.TableBody(row('a', 'b', 'c')))
    assert table.cols == 3
    assert table.colspec == [('AlignDefault', 'ColWidthDefault')] * 3


def test_table_columns_count_colspans():
    table = pf.Table(pf.TableBody(pf.TableRow(cell('a', colspan=2), cell('b'))))
    assert table.cols == 3


def test_table_columns_inferred_from_head_when_no_body():
    table = pf.Table(head=pf.TableHead(row('a', 'b')))
    assert table.cols == 2
    assert len(table.colspec) == 2
    empty = pf.Table()
    assert empty.cols == 0 and empty.colspec == []


def test_table_column_mismatch_raises_index_error():
    with pytest.raises(IndexError):
        pf.Table(pf.TableBody(row('a', 'b')), head=pf.TableHead(row('a')))
    with pytest.raises(IndexError):
        pf.Table(pf.TableBody(row('a', 'b')), foot=pf.TableFoot(row('a', 'b', 'c')))
    with pytest.raises(IndexError):
        pf.Table(pf.TableBody(row('a', 'b')), colspec=[('AlignLeft', 0.5)])


def test_table_colspec_validation():
    table = pf.Table(pf.TableBody(row('a', 'b')),
                     colspec=[('AlignLeft', 0.25), ('AlignRight', 'ColWidthDefault')])
    assert table.colspec == [('AlignLeft', 0.25), ('AlignRight', 'ColWidthDefault')]
    assert to_json_value(table)['c'][2] == [
        [{'t': 'AlignLeft'}, {'t': 'ColWidth', 'c': 0.25}],
        [{'t': 'AlignRight'}, {'t': 'ColWidthDefault'}]]
    assert pf.Table(pf.TableBody(row('a')), colspec=[('AlignCenter', 1)]).colspec == [('AlignCenter', 1)]
    with pytest.raises(TypeError):
        pf.Table(pf.TableBody(row('a')), colspec=[('Left', 0.5)])
    with pytest.raises(TypeError):
        pf.Table(pf.TableBody(row('a')), colspec=[('AlignLeft', '50%')])


def test_table_parts_types_checked():
    with pytest.raises(TypeError):
        pf.Table(row('a'))
    with pytest.raises(TypeError):
        pf.Table(head=pf.TableFoot())
    with pytest.raises(TypeError):
        pf.Table(foot=pf.TableHead())
    with pytest.raises(TypeError):
        pf.Table(caption=pf.Para())
    with pytest.raises(TypeError):
        pf.TableHead(cell())
    with pytest.raises(TypeError):
        pf.TableBody(cell())
    with pytest.raises(TypeError):
        pf.TableBody(head=[cell()])
    with pytest.raises(TypeError):
        pf.TableRow(pf.Para())
    with pytest.raises(TypeError):
        pf.TableCell(pf.Str('inline'))
    with pytest.raises(TypeError):
        pf.TableBody(row_head_columns='1')


@pytest.mark.parametrize('kwargs', [{'rowspan': 0}, {'colspan': 0}, {'rowspan': -1}])
def test_cell_spans_must_be_positive(kwargs):
    with pytest.raises(TypeError):
        pf.TableCell(**kwargs)


def test_table_defaults_and_parent_links():
    body = pf.TableBody(row('a'))
    table = pf.Table(body)
    assert isinstance(table.head, pf.TableHead) and len(table.head.content) == 0
    assert isinstance(table.foot, pf.TableFoot) and len(table.foot.content) == 0
    assert isinstance(table.caption, pf.Caption)
    assert table.caption.short_caption is None
    assert (table.head.parent, table.head.location) == (table, 'head')
    assert (table.foot.parent, table.foot.location) == (table, 'foot')
    assert (table.caption.parent, table.caption.location) == (table, 'caption')
    assert table.content[0] is body and body.parent is table
    assert body.head.location == 'head' and body.head.parent is body
    c = table.content[0].content[0].content[0]
    assert c.parent.parent is body
    assert c.ancestor(3) is table


def test_table_setters():
    table = pf.Table(pf.TableBody(row('a', 'b')))
    table.head = pf.TableHead(row('h1', 'h2'))
    assert table.head.parent is table
    table.foot = None
    assert isinstance(table.foot, pf.TableFoot)
    table.caption = pf.Caption(pf.Plain(pf.Str('cap')))
    assert table.caption.parent is table
    with pytest.raises(IndexError):
        table.head = pf.TableHead(row('h1'))


def test_table_body_head_setter():
    body = pf.TableBody()
    body.head = [row('a')]
    assert len(body.head) == 1 and body.head.location == 'head'
    body.head = body.head
    assert len(body.head) == 1
    body.head = None
    assert len(body.head) == 0


def test_caption_short_caption():
    cap = pf.Caption(pf.Plain(pf.Str('long')), short_caption=[pf.Str('short')])
    assert cap.short_caption.location == 'short_caption'
    assert cap.short_caption[0].parent is cap
    assert to_json_value(cap) == [[{'t': 'Str', 'c': 'short'}],
                                  [{'t': 'Plain', 'c': [{'t': 'Str', 'c': 'long'}]}]]
    cap.short_caption = None
    assert to_json_value(cap) == [None, [{'t': 'Plain', 'c': [{'t': 'Str', 'c': 'long'}]}]]
    cap.short_caption = pf.Caption(short_caption=[pf.Str('x')]).short_caption
    assert cap.short_caption[0].text == 'x'


def test_table_full_json_roundtrip():
    table = pf.Table(
        pf.TableBody(row('b1', 'b2'), head=[row('i1', 'i2')], row_head_columns=1,
                     identifier='body', classes=['bc'], attributes={'k': 'v'}),
        pf.TableBody(row('c1', 'c2')),
        head=pf.TableHead(row('h1', 'h2', identifier='hr'), identifier='head'),
        foot=pf.TableFoot(pf.TableRow(cell('f', colspan=2, alignment='AlignCenter')), classes=['foot']),
        caption=pf.Caption(pf.Para(pf.Str('Caption')), short_caption=[pf.Str('Short')]),
        colspec=[('AlignLeft', 0.3), ('AlignRight', 0.7)],
        identifier='t', classes=['tc'], attributes={'a': 'b'},
    )
    back = roundtrip(table)
    assert back == table
    assert to_json_value(back) == to_json_value(table)
    j = to_json_value(table)['c']
    assert j[0] == ['t', ['tc'], [['a', 'b']]]
    assert j[1][0] == [{'t': 'Str', 'c': 'Short'}]
    assert j[3][0] == ['head', [], []]
    assert j[4][0][:2] == [['body', ['bc'], [['k', 'v']]], 1]
    assert len(j[4][0][2]) == 1 and len(j[4][0][3]) == 1
    assert j[5][1][0][1][0][1:4] == [{'t': 'AlignCenter'}, 1, 2]


def test_table_from_json_helpers():
    raw_cell = [['', [], []], 'AlignRight', 2, 1, []]
    c = cell_from_json(raw_cell)
    assert (c.alignment, c.rowspan, c.colspan) == ('AlignRight', 2, 1)
    assert colspec_to_json('ColWidthDefault') == {'t': 'ColWidthDefault'}
    assert colspec_to_json(0.5) == {'t': 'ColWidth', 'c': 0.5}
    assert count_columns_in_row([cell(colspan=2), cell()]) == 3
    assert count_columns_in_row([]) == 0
    empty_attr = ['', [], []]
    table = table_from_json([empty_attr, [None, []], [['AlignDefault', 'ColWidthDefault']],
                             [empty_attr, []], [[empty_attr, 0, [], [[empty_attr, [raw_cell[:1] + ['AlignDefault', 1, 1, []]]]]]],
                             [empty_attr, []]])
    assert isinstance(table, pf.Table) and table.cols == 1


def test_tables_from_corpus():
    doc = load_path(JSON_FIXTURES / 'tables-html.json')
    tables = [b for b in doc.content if isinstance(b, pf.Table)]
    assert len(tables) == 2
    t = tables[0]
    assert (t.identifier, t.classes, t.attributes) == ('html-table', ['data', 'wide'], {'source': 'test'})
    assert t.cols == 3
    assert [w for _, w in t.colspec] == [0.25, 0.25, 0.5]
    assert len(t.head.content) == 2
    assert [c.rowspan for c in t.head.content[0].content] == [2, 1]
    assert [c.colspan for c in t.head.content[0].content] == [1, 2]
    assert len(t.content) == 2
    assert t.content[1].classes == ['second-body']
    assert [b.row_head_columns for b in t.content] == [1, 1]
    assert len(t.foot.content) == 1
    assert pf.stringify(t.caption) == 'An HTML table caption'
