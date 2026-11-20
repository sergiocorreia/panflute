"""
Unit tests for the element classes in panflute.elements / panflute.table_elements:
construction from Python, exact JSON produced by to_json(), JSON -> element
round trips, equality, attribute access, and type checking of children.
"""

import json

import pytest

import panflute as pf
from panflute.elements import builtin2meta, from_json

from .helpers import roundtrip, to_json_value


EMPTY_ATTR = ['', [], []]


def S(text):
    return {'t': 'Str', 'c': text}


SPACE = {'t': 'Space'}


# (element built from Python, exact JSON expected from to_json)
CASES = {
    'Null': (pf.Null(), {'t': 'Null'}),
    'Space': (pf.Space(), {'t': 'Space'}),
    'SoftBreak': (pf.SoftBreak(), {'t': 'SoftBreak'}),
    'LineBreak': (pf.LineBreak(), {'t': 'LineBreak'}),
    'HorizontalRule': (pf.HorizontalRule(), {'t': 'HorizontalRule'}),
    'Str': (pf.Str('héllo'), S('héllo')),
    'Plain': (pf.Plain(pf.Str('a'), pf.Space), {'t': 'Plain', 'c': [S('a'), SPACE]}),
    'Para': (pf.Para(pf.Str('a')), {'t': 'Para', 'c': [S('a')]}),
    'BlockQuote': (pf.BlockQuote(pf.Para(pf.Str('q'))),
                   {'t': 'BlockQuote', 'c': [{'t': 'Para', 'c': [S('q')]}]}),
    'Emph': (pf.Emph(pf.Str('e')), {'t': 'Emph', 'c': [S('e')]}),
    'Strong': (pf.Strong(pf.Str('s')), {'t': 'Strong', 'c': [S('s')]}),
    'Underline': (pf.Underline(pf.Str('u')), {'t': 'Underline', 'c': [S('u')]}),
    'Strikeout': (pf.Strikeout(pf.Str('x')), {'t': 'Strikeout', 'c': [S('x')]}),
    'Superscript': (pf.Superscript(pf.Str('2')), {'t': 'Superscript', 'c': [S('2')]}),
    'Subscript': (pf.Subscript(pf.Str('i')), {'t': 'Subscript', 'c': [S('i')]}),
    'SmallCaps': (pf.SmallCaps(pf.Str('sc')), {'t': 'SmallCaps', 'c': [S('sc')]}),
    'Note': (pf.Note(pf.Para(pf.Str('n'))), {'t': 'Note', 'c': [{'t': 'Para', 'c': [S('n')]}]}),
    'Header': (pf.Header(pf.Str('h'), level=3, identifier='id', classes=['a', 'b'],
                         attributes={'k': 'v', 'k2': 'v2'}),
               {'t': 'Header', 'c': [3, ['id', ['a', 'b'], [['k', 'v'], ['k2', 'v2']]], [S('h')]]}),
    'Div': (pf.Div(pf.Para(pf.Str('d')), identifier='x', classes=['c']),
            {'t': 'Div', 'c': [['x', ['c'], []], [{'t': 'Para', 'c': [S('d')]}]]}),
    'Span': (pf.Span(pf.Str('s'), attributes={'a': '1'}),
             {'t': 'Span', 'c': [['', [], [['a', '1']]], [S('s')]]}),
    'Quoted': (pf.Quoted(pf.Str('q'), quote_type='SingleQuote'),
               {'t': 'Quoted', 'c': [{'t': 'SingleQuote'}, [S('q')]]}),
    'Cite': (pf.Cite(pf.Str('@k'), citations=[pf.Citation('k', mode='AuthorInText',
                                                           prefix=[pf.Str('p')], suffix=[pf.Str('s')],
                                                           hash=2, note_num=1)]),
             {'t': 'Cite', 'c': [[{'citationSuffix': [S('s')], 'citationNoteNum': 1,
                                   'citationMode': {'t': 'AuthorInText'},
                                   'citationPrefix': [S('p')], 'citationId': 'k',
                                   'citationHash': 2}],
                                 [S('@k')]]}),
    'Link': (pf.Link(pf.Str('l'), url='http://x', title='t', classes=['c']),
             {'t': 'Link', 'c': [['', ['c'], []], [S('l')], ['http://x', 't']]}),
    'Image': (pf.Image(pf.Str('alt'), url='a.png', title='t', identifier='i'),
              {'t': 'Image', 'c': [['i', [], []], [S('alt')], ['a.png', 't']]}),
    'Code': (pf.Code('x = 1', classes=['py']),
             {'t': 'Code', 'c': [['', ['py'], []], 'x = 1']}),
    'CodeBlock': (pf.CodeBlock('code\nblock', identifier='cb', attributes={'n': '1'}),
                  {'t': 'CodeBlock', 'c': [['cb', [], [['n', '1']]], 'code\nblock']}),
    'RawBlock': (pf.RawBlock('<hr>', format='html'), {'t': 'RawBlock', 'c': ['html', '<hr>']}),
    'RawInline': (pf.RawInline(r'\x', format='latex'), {'t': 'RawInline', 'c': ['latex', r'\x']}),
    'Math': (pf.Math('x^2', format='InlineMath'),
             {'t': 'Math', 'c': [{'t': 'InlineMath'}, 'x^2']}),
    'BulletList': (pf.BulletList(pf.ListItem(pf.Plain(pf.Str('a'))), pf.ListItem()),
                   {'t': 'BulletList', 'c': [[{'t': 'Plain', 'c': [S('a')]}], []]}),
    'OrderedList': (pf.OrderedList(pf.ListItem(pf.Plain(pf.Str('a'))), start=3,
                                   style='LowerRoman', delimiter='TwoParens'),
                    {'t': 'OrderedList', 'c': [[3, {'t': 'LowerRoman'}, {'t': 'TwoParens'}],
                                               [[{'t': 'Plain', 'c': [S('a')]}]]]}),
    'DefinitionList': (pf.DefinitionList(pf.DefinitionItem(
                           [pf.Str('t')], [pf.Definition(pf.Plain(pf.Str('d'))), pf.Definition()])),
                       {'t': 'DefinitionList', 'c': [[[S('t')], [[{'t': 'Plain', 'c': [S('d')]}], []]]]}),
    'LineBlock': (pf.LineBlock(pf.LineItem(pf.Str('l')), pf.LineItem()),
                  {'t': 'LineBlock', 'c': [[S('l')], []]}),
    'Figure': (pf.Figure(pf.Plain(pf.Str('f')), caption=pf.Caption(pf.Plain(pf.Str('c'))),
                         identifier='fig'),
               {'t': 'Figure', 'c': [['fig', [], []], [None, [{'t': 'Plain', 'c': [S('c')]}]],
                                     [{'t': 'Plain', 'c': [S('f')]}]]}),
    'MetaString': (pf.MetaString('s'), {'t': 'MetaString', 'c': 's'}),
    'MetaBool': (pf.MetaBool(False), {'t': 'MetaBool', 'c': False}),
    'MetaInlines': (pf.MetaInlines(pf.Str('i')), {'t': 'MetaInlines', 'c': [S('i')]}),
    'MetaBlocks': (pf.MetaBlocks(pf.Para(pf.Str('b'))),
                   {'t': 'MetaBlocks', 'c': [{'t': 'Para', 'c': [S('b')]}]}),
    'MetaList': (pf.MetaList(pf.MetaString('a'), True),
                 {'t': 'MetaList', 'c': [{'t': 'MetaString', 'c': 'a'}, {'t': 'MetaBool', 'c': True}]}),
    'MetaMap': (pf.MetaMap(a=pf.MetaString('x'), b=pf.MetaMap()),
                {'t': 'MetaMap', 'c': {'a': {'t': 'MetaString', 'c': 'x'},
                                       'b': {'t': 'MetaMap', 'c': {}}}}),
    'Table': (pf.Table(pf.TableBody(pf.TableRow(pf.TableCell(pf.Plain(pf.Str('c')))))),
              {'t': 'Table', 'c': [
                  EMPTY_ATTR, [None, []],
                  [[{'t': 'AlignDefault'}, {'t': 'ColWidthDefault'}]],
                  [EMPTY_ATTR, []],
                  [[EMPTY_ATTR, 0, [], [[EMPTY_ATTR, [[EMPTY_ATTR, {'t': 'AlignDefault'}, 1, 1,
                                                        [{'t': 'Plain', 'c': [S('c')]}]]]]]]],
                  [EMPTY_ATTR, []]]}),
}

# Elements that are not standalone pandoc objects: their JSON is a bare list/dict
SUB_ELEMENTS = {
    'ListItem': (pf.ListItem(pf.Plain(pf.Str('a'))), [{'t': 'Plain', 'c': [S('a')]}]),
    'Definition': (pf.Definition(pf.Plain(pf.Str('d'))), [{'t': 'Plain', 'c': [S('d')]}]),
    'DefinitionItem': (pf.DefinitionItem([pf.Str('t')], []), [[S('t')], []]),
    'LineItem': (pf.LineItem(pf.Str('l'), pf.Space), [S('l'), SPACE]),
    'Citation': (pf.Citation('id'),
                 {'citationSuffix': [], 'citationNoteNum': 0, 'citationMode': {'t': 'NormalCitation'},
                  'citationPrefix': [], 'citationId': 'id', 'citationHash': 0}),
    'Caption': (pf.Caption(pf.Plain(pf.Str('c')), short_caption=[pf.Str('s')]),
                [[S('s')], [{'t': 'Plain', 'c': [S('c')]}]]),
    'TableHead': (pf.TableHead(identifier='h'), [['h', [], []], []]),
    'TableFoot': (pf.TableFoot(classes=['f']), [['', ['f'], []], []]),
    'TableRow': (pf.TableRow(pf.TableCell(), attributes={'a': 'b'}),
                 [['', [], [['a', 'b']]], [[EMPTY_ATTR, {'t': 'AlignDefault'}, 1, 1, []]]]),
    # TableBody.to_json() wraps its JSON in a {'t': 'TableBody'} object, but Table
    # serialises its bodies with TableBody._slots_to_json(), as pandoc expects.
    'TableBody': (pf.TableBody(head=[pf.TableRow()], row_head_columns=1, identifier='b'),
                  {'t': 'TableBody', 'c': [['b', [], []], 1, [[EMPTY_ATTR, []]], []]}),
    'TableCell': (pf.TableCell(pf.Plain(pf.Str('x')), alignment='AlignRight', rowspan=2, colspan=3),
                  [EMPTY_ATTR, {'t': 'AlignRight'}, 2, 3, [{'t': 'Plain', 'c': [S('x')]}]]),
}


@pytest.mark.parametrize('name', sorted(CASES))
def test_to_json(name):
    elem, expected = CASES[name]
    assert to_json_value(elem) == expected
    assert elem.tag == name


@pytest.mark.parametrize('name', sorted(SUB_ELEMENTS))
def test_sub_element_to_json(name):
    elem, expected = SUB_ELEMENTS[name]
    assert to_json_value(elem) == expected
    assert elem.tag == name


@pytest.mark.parametrize('name', sorted(CASES))
def test_json_roundtrip(name):
    elem, expected = CASES[name]
    back = roundtrip(elem)
    assert type(back) is type(elem)
    assert back == elem
    assert to_json_value(back) == expected


def test_every_public_element_class_is_tested():
    classes = {name for name in dir(pf)
               if isinstance(getattr(pf, name), type) and issubclass(getattr(pf, name), pf.Element)}
    assert classes - set(CASES) - set(SUB_ELEMENTS) == {'Element', 'Block', 'Inline', 'MetaValue', 'Doc'}


def test_class_hierarchy():
    for name in ['Null', 'HorizontalRule', 'Plain', 'Para', 'BlockQuote', 'Header', 'Div',
                 'CodeBlock', 'RawBlock', 'BulletList', 'OrderedList', 'DefinitionList',
                 'LineBlock', 'Figure', 'Table', 'TableHead', 'TableFoot', 'TableBody']:
        assert issubclass(getattr(pf, name), pf.Block), name
    for name in ['Space', 'SoftBreak', 'LineBreak', 'Str', 'Emph', 'Strong', 'Underline',
                 'Strikeout', 'Superscript', 'Subscript', 'SmallCaps', 'Note', 'Span', 'Quoted',
                 'Cite', 'Link', 'Image', 'Code', 'Math', 'RawInline']:
        assert issubclass(getattr(pf, name), pf.Inline), name
    for name in ['MetaString', 'MetaBool', 'MetaInlines', 'MetaBlocks', 'MetaList', 'MetaMap']:
        assert issubclass(getattr(pf, name), pf.MetaValue), name
    for name in ['Doc', 'Citation', 'ListItem', 'Definition', 'DefinitionItem', 'LineItem',
                 'TableRow', 'TableCell', 'Caption']:
        cls = getattr(pf, name)
        assert issubclass(cls, pf.Element)
        assert not issubclass(cls, (pf.Block, pf.Inline, pf.MetaValue)), name


# ---------------------------------------------------------------------------
# Defaults and attribute access
# ---------------------------------------------------------------------------

def test_defaults():
    h = pf.Header()
    assert (h.level, h.identifier, h.classes, h.attributes) == (1, '', [], {})
    assert list(h.content) == []
    link = pf.Link()
    assert (link.url, link.title) == ('', '')
    assert pf.Image().url == ''
    assert pf.Quoted().quote_type == 'DoubleQuote'
    assert pf.Math('x').format == 'DisplayMath'
    assert pf.RawBlock('x').format == 'html'
    assert pf.RawInline('x').format == 'html'
    ol = pf.OrderedList()
    assert (ol.start, ol.style, ol.delimiter) == (1, 'Decimal', 'Period')
    c = pf.Citation('id')
    assert (c.mode, c.hash, c.note_num, list(c.prefix), list(c.suffix)) == ('NormalCitation', 0, 0, [], [])
    assert pf.Cite().citations.list == []
    fig = pf.Figure()
    assert isinstance(fig.caption, pf.Caption) and fig.caption.short_caption is None
    cell = pf.TableCell()
    assert (cell.alignment, cell.rowspan, cell.colspan) == ('AlignDefault', 1, 1)


def test_mutable_default_arguments_are_not_shared():
    a, b = pf.Div(), pf.Div()
    a.classes.append('x')
    a.attributes['k'] = 'v'
    assert b.classes == [] and b.attributes == {}
    assert pf.Div().classes == [] and pf.Div().attributes == {}
    d1, d2 = pf.Doc(), pf.Doc()
    d1.metadata['k'] = 'v'
    assert 'k' not in d2.metadata


def test_attributes_are_copied_into_a_dict_preserving_order():
    attrs = [('z', '1'), ('a', '2')]
    span = pf.Span(attributes=attrs)
    assert span.attributes == {'z': '1', 'a': '2'}
    assert list(span.attributes) == ['z', 'a']
    original = {'k': 'v'}
    span = pf.Span(attributes=original)
    span.attributes['k'] = 'changed'
    assert original == {'k': 'v'}


def test_attribute_edits_reach_json():
    h = pf.Header(pf.Str('x'))
    h.level += 1
    h.identifier = 'new'
    h.classes.append('c')
    h.attributes['k'] = 'v'
    assert to_json_value(h) == {'t': 'Header', 'c': [2, ['new', ['c'], [['k', 'v']]], [S('x')]]}
    s = pf.Str('a')
    s.text = 'b'
    assert to_json_value(s) == S('b')


def test_content_setter_accepts_lists_and_containers():
    p = pf.Para(pf.Str('a'))
    p.content = [pf.Str('b'), pf.Space]
    assert to_json_value(p) == {'t': 'Para', 'c': [S('b'), SPACE]}
    q = pf.Para()
    q.content = p.content
    assert to_json_value(q) == to_json_value(p)
    assert q.content[0].parent is q
    with pytest.raises(TypeError):
        p.content = [pf.Para()]


def test_named_list_setters_accept_lists_and_containers():
    para = pf.Para(pf.Str('s'), pf.Space)
    c = pf.Citation('id')
    c.hash = 100
    c.suffix = para.content
    c.prefix = [pf.Str('p')]
    assert [e.tag for e in c.suffix] == ['Str', 'Space']
    assert c.suffix[0].parent is c and c.suffix.location == 'suffix'
    assert to_json_value(c)['citationSuffix'] == [S('s'), SPACE]
    assert to_json_value(c)['citationHash'] == 100
    cite = pf.Cite()
    cite.citations = pf.Cite(citations=[c]).citations
    assert cite.citations[0].parent is cite
    di = pf.DefinitionItem([], [])
    di.term = para.content
    di.definitions = [pf.Definition()]
    assert di.term[0].parent is di and di.term.location == 'term'
    assert di.definitions[0].parent is di and di.definitions.location == 'definitions'
    with pytest.raises(TypeError):
        c.prefix = [pf.Para()]
    with pytest.raises(TypeError):
        di.definitions = [pf.Para()]


def test_class_names_accepted_in_place_of_instances():
    # check_type calls callables, so `Space` works as `Space()`
    p = pf.Para(pf.Str('a'), pf.Space, pf.SoftBreak)
    assert [type(x) for x in p.content] == [pf.Str, pf.Space, pf.SoftBreak]
    p.content.append(pf.LineBreak)
    assert type(p.content[-1]) is pf.LineBreak


def test_text_elements():
    for cls in (pf.Str, pf.Code, pf.CodeBlock, pf.RawBlock, pf.RawInline, pf.Math, pf.MetaString):
        elem = cls('txt')
        assert elem.text == 'txt'
        with pytest.raises(TypeError):
            cls(1)


def test_tag_property():
    assert pf.Str('a').tag == 'Str'
    assert pf.Doc().tag == 'Doc'

    class MyStr(pf.Str):
        __slots__ = []

    assert MyStr('x').tag == 'MyStr'


# ---------------------------------------------------------------------------
# Type checking
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('build', [
    lambda: pf.Para(pf.Para()),                 # block inside inline container
    lambda: pf.Para('text'),                    # str instead of Str
    lambda: pf.Div(pf.Str('x')),                # inline inside block container
    lambda: pf.Note(pf.Str('x')),               # Note holds blocks
    lambda: pf.BulletList(pf.Para()),           # needs ListItem
    lambda: pf.OrderedList(pf.Para()),
    lambda: pf.DefinitionList(pf.Para()),       # needs DefinitionItem
    lambda: pf.DefinitionItem([pf.Para()], []),
    lambda: pf.DefinitionItem([], [pf.Para()]),  # needs Definition
    lambda: pf.LineBlock(pf.Str('x')),          # needs LineItem
    lambda: pf.LineItem(pf.Para()),
    lambda: pf.Cite(citations=[pf.Str('x')]),
    lambda: pf.Citation(1),
    lambda: pf.Citation('id', prefix=[pf.Para()]),
    lambda: pf.Header(level='1'),
    lambda: pf.Header(level=0),
    lambda: pf.Header(level=11),
    lambda: pf.Header(identifier=1),
    lambda: pf.Div(classes=[1]),
    lambda: pf.Link(url=None),
    lambda: pf.Image(title=1),
    lambda: pf.MetaInlines(pf.Para()),
    lambda: pf.MetaBlocks(pf.Str('x')),
    lambda: pf.MetaBool('yes'),
    lambda: pf.MetaString(1),
    lambda: pf.MetaList(object()),
    lambda: pf.MetaMap(k=object()),
    lambda: pf.Doc(pf.Str('x')),
    lambda: pf.Figure(pf.Str('x')),
    lambda: pf.Figure(caption=pf.Para()),
    lambda: pf.Caption(pf.Str('x')),
    lambda: pf.Caption(short_caption=[pf.Para()]),
    lambda: pf.OrderedList(start='1'),
])
def test_wrong_child_types_raise_type_error(build):
    with pytest.raises(TypeError):
        build()


@pytest.mark.parametrize('build', [
    lambda: pf.Quoted(quote_type='Triple'),
    lambda: pf.Math('x', format='Inline'),
    lambda: pf.OrderedList(style='Roman'),
    lambda: pf.OrderedList(delimiter='Dot'),
    lambda: pf.Citation('id', mode='Normal'),
    lambda: pf.TableCell(alignment='Left'),
    # (RawBlock/RawInline accept any format string: see test_regressions.py, #236/#247)
])
def test_values_outside_enumerations_raise_type_error(build):
    with pytest.raises(TypeError):
        build()


def test_type_error_message_names_the_element():
    with pytest.raises(TypeError, match='Element "Para" received "Para"'):
        pf.Para(pf.Para())
    with pytest.raises(TypeError, match='Element "Emph" received "str"'):
        pf.Emph('x')


def test_header_levels_accepted():
    assert [pf.Header(level=n).level for n in (1, 6, 10)] == [1, 6, 10]


def test_raw_formats_accepted():
    from panflute.elements import RAW_FORMATS
    for fmt in ['html', 'tex', 'latex', 'context', 'typst', 'openxml', 'markdown', 'rst', 'json',
                'latex-merge', 'noteref']:
        assert fmt in RAW_FORMATS
        assert pf.RawInline('x', format=fmt).format == fmt
        assert pf.RawBlock('x', format=fmt).format == fmt


# ---------------------------------------------------------------------------
# Equality
# ---------------------------------------------------------------------------

def test_equality_by_value():
    assert pf.Str('a') == pf.Str('a')
    assert pf.Str('a') != pf.Str('b')
    assert pf.Space() == pf.Space()
    assert pf.Space() != pf.SoftBreak()
    assert pf.Str('a') != pf.MetaString('a')
    assert pf.Para(pf.Str('a')) == pf.Para(pf.Str('a'))
    assert pf.Para(pf.Str('a')) != pf.Plain(pf.Str('a'))
    assert pf.Para(pf.Str('a')) != pf.Para(pf.Str('a'), pf.Space)
    assert pf.Header(level=1) != pf.Header(level=2)
    assert pf.Div(classes=['a']) != pf.Div(classes=['b'])
    assert pf.Para() != None  # noqa: E711
    assert pf.Str('a') != 'a'


def test_equality_ignores_position_in_tree():
    a = pf.Str('x')
    b = pf.Str('x')
    pf.Para(pf.Space, a)
    assert a.index == 1 and b.index is None
    assert a == b


def test_equality_compares_nested_content():
    def build(word):
        return pf.Doc(pf.Div(pf.Para(pf.Emph(pf.Str(word)))), metadata={'k': 'v'})
    assert build('x') == build('x')
    assert build('x') != build('y')


def test_doc_equality():
    text = {'pandoc-api-version': [1, 23], 'meta': {'author': {'t': 'MetaInlines', 'c': [S('Bob')]}},
            'blocks': [{'t': 'Header', 'c': [1, ['h', [], []], [S('Header')]]},
                       {'t': 'Para', 'c': [S('text')]}]}
    doc1, doc2, doc3 = (json.loads(json.dumps(text), object_hook=from_json) for _ in range(3))
    assert doc1 == doc2 == doc3

    doc2.content[0].content[0].text = 'Changed'
    assert doc1 != doc2
    assert doc1 == doc3

    doc3.metadata['author'] = pf.MetaInlines(pf.Str('John'))
    assert doc1 != doc3
    doc3.metadata['author'] = pf.MetaInlines(pf.Str('Bob'))
    assert doc1 == doc3

    assert doc1.content != doc2.content
    assert doc1.content == doc3.content

    # format and api_version are not part of Doc equality
    doc3.format = 'latex'
    doc3.api_version = (1, 22)
    assert doc1 == doc3
    assert doc1 != pf.Para()


# ---------------------------------------------------------------------------
# repr
# ---------------------------------------------------------------------------

def test_repr():
    assert repr(pf.Str('a')) == 'Str(a)'
    assert repr(pf.Space()) == 'Space'
    assert repr(pf.Para(pf.Str('a'), pf.Space)) == 'Para(Str(a) Space)'
    assert repr(pf.Header(pf.Str('h'), level=2, identifier='i')) == "Header(Str(h); level=2, identifier='i')"
    assert repr(pf.Math('x', format='InlineMath')) == "Math(x; format='InlineMath')"
    assert repr(pf.RawInline(r'\a', format='tex')) == r"RawInline(\a; format='tex')"
    assert repr(pf.MetaString('m')) == 'MetaString(m)'
    assert repr(pf.MetaBool(True)) == 'MetaBool(True)'
    assert repr(pf.DefinitionItem([pf.Str('t')], [])) == 'DefinitionItem(ListContainer(Str(t)): ListContainer())'
    assert repr(pf.Para().content) == 'ListContainer()'


# ---------------------------------------------------------------------------
# Doc
# ---------------------------------------------------------------------------

def test_doc_construction():
    doc = pf.Doc(pf.Para(pf.Str('a')), metadata={'title': 'T', 'flag': True, 'n': 1.5,
                                                 'items': [1, 'b'], 'map': {'k': False}},
                 format='latex', api_version=(1, 22, 1))
    assert doc.format == 'latex'
    assert doc.api_version == (1, 22, 1)
    assert isinstance(doc.metadata, pf.MetaMap)
    assert to_json_value(doc) == {
        'pandoc-api-version': [1, 22, 1],
        'meta': {
            'title': {'t': 'MetaString', 'c': 'T'},
            'flag': {'t': 'MetaBool', 'c': True},
            'n': {'t': 'MetaString', 'c': '1.5'},
            'items': {'t': 'MetaList', 'c': [{'t': 'MetaString', 'c': '1'}, {'t': 'MetaString', 'c': 'b'}]},
            'map': {'t': 'MetaMap', 'c': {'k': {'t': 'MetaBool', 'c': False}}},
        },
        'blocks': [{'t': 'Para', 'c': [S('a')]}],
    }


def test_doc_defaults():
    doc = pf.Doc()
    assert doc.format == 'html'
    assert doc.api_version == (1, 23)
    assert to_json_value(doc) == {'pandoc-api-version': [1, 23], 'meta': {}, 'blocks': []}
    assert doc.pandoc_version is None
    assert doc.pandoc_reader_options == {}


@pytest.mark.parametrize('version', [(1, 22), (1, 22, 0), (1, 23), (1, 23, 1), (1, 23, 1, 0), [1, 23, 1]])
def test_doc_api_versions_accepted(version):
    assert pf.Doc(api_version=version).api_version == tuple(version)


@pytest.mark.parametrize('version', [(1, 21), (1, 20), (1, 17, 0, 4), (1, 23, 0, 0, 1), ('1', '23'), None])
def test_doc_api_versions_rejected(version):
    with pytest.raises(TypeError):
        pf.Doc(api_version=version)


def test_doc_metadata_setter():
    doc = pf.Doc()
    doc.metadata = {'a': 'x'}
    assert doc.get_metadata('a') == 'x'
    doc.metadata = pf.MetaMap(b=pf.MetaBool(True))
    assert list(doc.metadata) == ['b']
    assert doc.metadata.parent is doc
    assert doc.metadata.location == 'metadata'


def test_doc_allows_extra_attributes():
    doc = pf.Doc()
    doc.counter = 3
    assert doc.counter == 3


# ---------------------------------------------------------------------------
# Metadata elements
# ---------------------------------------------------------------------------

class My_List(list):
    """Subclass for testing https://github.com/sergiocorreia/panflute/issues/166"""


class My_Dict(dict):
    """Subclass for testing https://github.com/sergiocorreia/panflute/issues/166"""


class Not_Builtin:
    pass


@pytest.mark.parametrize('value,expect_type', [
    ([], pf.MetaList),
    ({}, pf.MetaMap),
    (My_List(), pf.MetaList),
    (My_Dict(), pf.MetaMap),
    (1, pf.MetaString),
    (1.5, pf.MetaString),
    ('a', pf.MetaString),
    (True, pf.MetaBool),
    ([1], pf.MetaList),
    ({'a': My_List()}, pf.MetaMap),
    (pf.Para(), pf.MetaBlocks),
    (pf.Str('x'), pf.MetaInlines),
    (pf.MetaString('x'), pf.MetaString),
    (Not_Builtin(), Not_Builtin),
])
def test_builtin2meta(value, expect_type):
    assert type(builtin2meta(value)) is expect_type


def test_builtin2meta_values():
    assert builtin2meta(True) == pf.MetaBool(True)
    assert builtin2meta(0) == pf.MetaString('0')
    assert builtin2meta(2.50) == pf.MetaString('2.5')
    assert builtin2meta(pf.Str('x')) == pf.MetaInlines(pf.Str('x'))
    assert builtin2meta(pf.Para()) == pf.MetaBlocks(pf.Para())
    assert to_json_value(builtin2meta({'a': [1, {'b': 'c'}]})) == {
        't': 'MetaMap', 'c': {'a': {'t': 'MetaList', 'c': [
            {'t': 'MetaString', 'c': '1'}, {'t': 'MetaMap', 'c': {'b': {'t': 'MetaString', 'c': 'c'}}}]}}}
    assert builtin2meta(None) is None
    with pytest.raises(TypeError):
        builtin2meta({'b': None})


def test_metalist_sequence_protocol():
    ml = pf.MetaList('a', True)
    assert len(ml) == 2
    assert ml[0] == pf.MetaString('a')
    assert ml[1] == pf.MetaBool(True)
    assert ml[-1] == pf.MetaBool(True)
    ml[0] = 'b'
    assert ml[0] == pf.MetaString('b')
    ml.append(3)
    ml.insert(0, False)
    assert [type(x).__name__ for x in ml] == ['MetaBool', 'MetaString', 'MetaBool', 'MetaString']
    del ml[0]
    assert len(ml) == 3
    assert ml[0].parent is ml
    assert list(reversed(ml))[0] == pf.MetaString('3')
    assert pf.MetaString('b') in ml
    ml.extend(['x'])
    assert ml.pop() == pf.MetaString('x')
    ml.content = [pf.MetaString('only')]
    assert to_json_value(ml) == {'t': 'MetaList', 'c': [{'t': 'MetaString', 'c': 'only'}]}


def test_metalist_index_method_258():
    S = pf.MetaString
    ml = pf.MetaList('a', 'b', True, 'a', {'k': 'v'}, ['x'])
    assert ml.index(S('a')) == 0
    assert ml.index(S('b')) == 1
    assert ml.index(pf.MetaBool(True)) == 2
    assert ml.index(pf.MetaMap(k='v')) == 4
    assert ml.index(pf.MetaList('x')) == 5
    item = ml[3]
    assert ml.index(item) == 0  # (found by ==, as in list.index)
    # start and stop, including negative values, as in list.index
    assert ml.index(S('a'), 1) == 3
    assert ml.index(S('a'), -3) == 3
    assert ml.index(S('a'), 0, 1) == 0
    assert ml.index(S('a'), 1, None) == 3
    assert ml.index(S('a'), 1, -2) == 3
    assert ml.index(S('a'), -100, 100) == 0
    as_list = [S('a'), S('b'), pf.MetaBool(True), S('a')]
    for args in [(S('a'), 1, 3), (S('a'), 4), (S('b'), 2), (S('a'), 1, -3), (S('zz'),), ('a',), (True,)]:
        with pytest.raises(ValueError):
            ml.index(*args)
        if len(args) > 1:
            with pytest.raises(ValueError):
                as_list.index(*args)
    with pytest.raises(TypeError):
        ml.index(S('a'), 'x')
    with pytest.raises(ValueError):
        pf.MetaList().index(S('a'))
    # It does not change the parent/index_in_parent of the items
    other = pf.MetaList()
    other.content.list.append(item)
    item.parent, item.index_in_parent = other, 0
    assert ml.index(S('b')) == 1
    assert item.parent is other and item.index_in_parent == 0


def test_metalist_mutable_sequence_api_258():
    from collections.abc import MutableSequence
    S = pf.MetaString
    ml = pf.MetaList('a', 'b', 'a')
    assert isinstance(ml, MutableSequence)
    assert S('a') in ml and S('z') not in ml and 'a' not in ml  # (items are MetaValues)
    assert ml.count(S('a')) == 2 and ml.count(S('z')) == 0
    assert list(reversed(ml)) == [S('a'), S('b'), S('a')]
    ml.remove(S('a'))  # (calls index(); it used to raise TypeError)
    assert list(ml) == [S('b'), S('a')]
    with pytest.raises(ValueError):
        ml.remove(S('z'))
    ml.extend(['c', pf.MetaBool(False)])
    assert list(ml) == [S('b'), S('a'), S('c'), pf.MetaBool(False)]
    same = ml
    ml += ['d']
    assert ml is same and ml[-1] == S('d')
    assert ml.pop() == S('d') and ml.pop(0) == S('b')
    with pytest.raises(IndexError):
        pf.MetaList().pop()
    ml.append('e')
    ml.reverse()
    assert list(ml) == [S('e'), pf.MetaBool(False), S('c'), S('a')]
    assert [e.index_in_parent for e in ml.content.list] == [0, 1, 2, 3]
    assert all(e.parent is ml for e in ml.content.list)
    ml.clear()
    assert len(ml) == 0 and not ml


def test_element_copy_and_pickle_keep_index_in_parent():
    import copy
    import pickle
    para = pf.Para(pf.Str('a'), pf.Emph(pf.Str('b')))
    doc = pf.Doc(para, metadata={'l': ['x', ['y']], 'm': {'k': 'v'}})
    emph = para.content[1]
    ml = doc.metadata['l']
    inner = ml[1]
    for clone in (copy.deepcopy, lambda x: pickle.loads(pickle.dumps(x))):
        e = clone(emph)
        assert e == emph and e.index_in_parent == 1 and e.index == 1 and type(e.parent) is pf.Para
        assert e.content[0].index_in_parent == 0
        m = clone(inner)
        assert m == inner and m.index_in_parent == 1 and m.index(pf.MetaString('y')) == 0
        d = clone(doc)
        assert d == doc and to_json_value(d) == to_json_value(doc)
        assert d.metadata['l'][1].index_in_parent == 1
    s = copy.copy(emph)
    assert s.index_in_parent == 1


def test_metamap_mapping_protocol():
    mm = pf.MetaMap(('a', 'x'), b=True)
    assert list(mm) == ['a', 'b']
    assert len(mm) == 2
    assert mm['a'] == pf.MetaString('x')
    assert mm['b'] == pf.MetaBool(True)
    mm['c'] = [1]
    assert isinstance(mm['c'], pf.MetaList)
    assert mm['c'].parent is mm
    del mm['a']
    assert 'a' not in mm and 'b' in mm
    assert dict(mm.items()) == {'b': pf.MetaBool(True), 'c': pf.MetaList('1')}
    assert mm.get('missing', 'default') == 'default'
    with pytest.raises(KeyError):
        mm['missing']
    mm.content = [('z', pf.MetaString('z'))]
    assert list(mm) == ['z']


def test_metamap_equality():
    assert pf.MetaMap(a='x') == pf.MetaMap(a='x')
    assert pf.MetaMap(a='x') != pf.MetaMap(a='y')
    assert pf.MetaMap(a='x', b='y') == pf.MetaMap(b='y', a='x')


def test_metabool_requires_bool():
    assert pf.MetaBool(True).boolean is True
    with pytest.raises(TypeError):
        pf.MetaBool(1)


# ---------------------------------------------------------------------------
# from_json
# ---------------------------------------------------------------------------

def test_from_json_special_values():
    for value in ['AlignLeft', 'ColWidthDefault', 'DisplayMath', 'SingleQuote', 'AuthorInText',
                  'Decimal', 'Period']:
        assert from_json({'t': value}) == value
    assert from_json({'t': 'ColWidth', 'c': 0.5}) == 0.5
    assert from_json({'k': 'v'}) == {'k': 'v'}


def test_from_json_accepts_legacy_empty_content():
    assert from_json({'t': 'Space', 'c': []}) == pf.Space()
    assert from_json({'t': 'Null'}) == pf.Null()


def test_from_json_unknown_tag():
    with pytest.raises(NotImplementedError, match='Unknown tag: Foo'):
        from_json({'t': 'Foo', 'c': []})


def test_from_json_legacy_unmeta():
    meta = from_json({'unMeta': {'a': pf.MetaString('x')}})
    assert isinstance(meta, pf.MetaMap) and meta['a'] == pf.MetaString('x')


def test_from_json_document():
    doc = json.loads('{"pandoc-api-version":[1,23,1],"meta":{"k":{"t":"MetaBool","c":true}},'
                     '"blocks":[{"t":"Para","c":[{"t":"Str","c":"x"}]}]}', object_hook=from_json)
    assert isinstance(doc, pf.Doc)
    assert doc.api_version == (1, 23, 1)
    assert doc.metadata['k'] == pf.MetaBool(True)
    assert doc.content[0] == pf.Para(pf.Str('x'))


def test_legacy_json_methods():
    # Serialisers for the pre-1.17 pandoc JSON format, kept for backwards compatibility
    assert pf.Quoted(pf.Str('q'))._slots_to_json_legacy() == [{'t': 'DoubleQuote', 'c': []}, [S('q')]]
    assert pf.Math('x')._slots_to_json_legacy() == [{'t': 'DisplayMath', 'c': []}, 'x']
    assert pf.OrderedList()._slots_to_json_legacy() == [
        [1, {'t': 'Decimal', 'c': []}, {'t': 'Period', 'c': []}], []]
    assert pf.Citation('id').to_json_legacy() == {
        'citationSuffix': [], 'citationNoteNum': 0, 'citationMode': {'t': 'NormalCitation', 'c': []},
        'citationPrefix': [], 'citationId': 'id', 'citationHash': 0}


@pytest.mark.parametrize('start', [0, 1, 7, -2])
def test_ordered_list_start_roundtrip(start):
    raw = {'t': 'OrderedList', 'c': [[start, {'t': 'Example'}, {'t': 'OneParen'}], [[]]]}
    elem = json.loads(json.dumps(raw), object_hook=from_json)
    assert elem.start == start
    assert to_json_value(elem) == raw
