"""
Element navigation (parent, next, prev, offset, ancestor, container, doc)
and Element.walk() semantics, including replace_keyword.
"""

import pytest

import panflute as pf

from .helpers import to_json_value


def stringify_inline(elem):
    return elem.text if isinstance(elem, pf.Str) else ' '


def build_doc():
    """
    Doc
      Para: Str(a) Space Emph(Str(b)) Str(c)
      Div
        Plain: Str(d)
      BulletList
        ListItem: Plain: Str(e)
        ListItem: Plain: Str(f)
    """
    return pf.Doc(
        pf.Para(pf.Str('a'), pf.Space, pf.Emph(pf.Str('b')), pf.Str('c')),
        pf.Div(pf.Plain(pf.Str('d'))),
        pf.BulletList(pf.ListItem(pf.Plain(pf.Str('e'))), pf.ListItem(pf.Plain(pf.Str('f')))),
        metadata={'title': pf.MetaInlines(pf.Str('t'))},
    )


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

def test_parent_chain_and_doc():
    doc = build_doc()
    para = doc.content[0]
    emph = para.content[2]
    b = emph.content[0]
    assert b.parent is emph and emph.parent is para and para.parent is doc
    assert doc.parent is None
    assert b.doc is doc and para.doc is doc and doc.doc is doc
    assert pf.Str('x').doc is None
    assert pf.Para(pf.Str('x')).content[0].doc is None


def test_ancestor():
    doc = build_doc()
    b = doc.content[0].content[2].content[0]
    assert b.ancestor(1) is b.parent
    assert b.ancestor(2) is doc.content[0]
    assert b.ancestor(3) is doc
    assert b.ancestor(4) is None
    assert b.ancestor(10) is None
    for bad in (0, -1, 1.0, '1'):
        with pytest.raises(TypeError):
            b.ancestor(bad)


def test_offset_next_prev():
    doc = build_doc()
    para = doc.content[0]
    a, space, emph, c = (para.content[i] for i in range(4))
    assert a.offset(0) is a
    assert a.next is space and space.next is emph and emph.next is c
    assert c.next is None
    assert a.prev is None
    assert c.prev is emph
    assert a.offset(3) is c
    assert a.offset(4) is None
    assert c.offset(-3) is a
    assert c.offset(-4) is None
    assert para.next is doc.content[1]
    assert doc.content[2].next is None
    assert doc.next is None and doc.prev is None
    assert pf.Str('loose').next is None


def test_offset_within_named_containers():
    cit_a, cit_b = pf.Citation('a'), pf.Citation('b')
    cite = pf.Cite(citations=[cit_a, cit_b])
    first = cite.citations[0]
    assert first.next.id == 'b'
    assert first.container is cite.citations
    di = pf.DefinitionItem([pf.Str('t1'), pf.Str('t2')],
                           [pf.Definition(pf.Plain(pf.Str('d1'))), pf.Definition()])
    d1 = di.definitions[0]
    assert d1.next is di.definitions[1]
    assert d1.parent is di and d1.location == 'definitions'
    assert di.term[0].next.text == 't2'
    assert di.term[0].location == 'term'


def test_container():
    doc = build_doc()
    para = doc.content[0]
    assert para.container is doc.content
    assert para.content[0].container is para.content
    assert doc.container is None
    assert pf.Str('x').container is None
    fig = pf.Figure(caption=pf.Caption())
    # Single-element attributes (captions, table heads/foots) have no container
    assert fig.caption.parent is fig and fig.caption.location == 'caption'
    assert fig.caption.container is None
    meta = doc.metadata['title']
    assert meta.container is doc.metadata.content


def test_index_after_access():
    doc = build_doc()
    assert [b.index for b in doc.content] == [0, 1, 2]
    items = doc.content[2].content
    assert [li.index for li in items] == [0, 1]
    assert items[1].prev is items[0]


# .index_in_parent (and its alias .index, except on MetaList: issue #258)

def test_index_in_parent_in_list_containers():
    doc = build_doc()
    para = doc.content[0]
    assert [e.index_in_parent for e in para.content] == [0, 1, 2, 3]
    assert para.index_in_parent == 0 and doc.content[2].index_in_parent == 2
    cite = pf.Cite(citations=[pf.Citation('a'), pf.Citation('b')])
    assert [c.index_in_parent for c in cite.citations] == [0, 1]
    di = pf.DefinitionItem([pf.Str('t1'), pf.Str('t2')], [pf.Definition(), pf.Definition()])
    assert [d.index_in_parent for d in di.definitions] == [0, 1]
    assert [t.index_in_parent for t in di.term] == [0, 1]


def test_index_in_parent_none_outside_list_containers():
    assert pf.Str('x').index_in_parent is None                       # detached
    assert pf.Doc().index_in_parent is None                          # the root
    fig = pf.Figure(caption=pf.Caption())
    assert fig.caption.index_in_parent is None                       # single child
    doc = build_doc()
    title = doc.metadata['title']
    assert title.parent is doc.metadata and title.index_in_parent is None  # value in a dict container
    mm = pf.MetaMap(a='x')
    assert mm['a'].index_in_parent is None and mm['a'].next is None


def test_index_in_parent_after_insert_delete_and_slice_assignment():
    para = pf.Para(*(pf.Str(c) for c in 'abcd'))
    a, b, c, d = para.content.list
    para.content.insert(1, pf.Str('new'))
    assert [e.index_in_parent for e in (a, b, c, d)] == [0, 2, 3, 4]
    del para.content[0]
    assert [e.index_in_parent for e in (b, c, d)] == [1, 2, 3]
    para.content[0:2] = [pf.Str('x')]
    assert [e.index_in_parent for e in (c, d)] == [1, 2]
    assert [e.index_in_parent for e in para.content] == [0, 1, 2]
    removed = para.content.pop()
    assert removed is d  # (still describes its last index)
    para.content.append(pf.Str('z'))
    assert para.content[-1].index_in_parent == 2


def test_index_in_parent_of_slice_items():
    para = pf.Para(*(pf.Str(c) for c in 'abcd'))
    items = para.content[1:3]
    assert [e.index_in_parent for e in items] == [1, 2]   # indexes in para.content
    assert items[0].index_in_parent == 1 and items[0].next.text == 'c'


def test_index_is_an_alias_of_index_in_parent():
    para = pf.Para(pf.Str('a'), pf.Str('b'))
    b = para.content[1]
    assert b.index == b.index_in_parent == 1
    b.index = 0
    assert b.index_in_parent == 0 and b.index == 0
    b.index_in_parent = 1
    assert b.index == 1
    s = pf.Str('x')
    assert s.index is None
    s.index = 3
    assert s.index_in_parent == 3
    doc = pf.Doc(pf.Para())
    assert doc.content[0].index == 0  # (Doc has a __dict__: the property still wins)
    doc.index = 5
    assert doc.index_in_parent == 5 and 'index' not in vars(doc)
    # Every other metadata element keeps .index
    mm = pf.MetaMap(a='x')
    ml = pf.MetaList(mm, pf.MetaInlines(pf.Str('s')), pf.MetaBlocks(pf.Para()))
    assert [ml[i].index for i in range(3)] == [0, 1, 2]


def test_metalist_index_in_parent_and_index_method():
    outer = pf.MetaList('a', pf.MetaList('b', 'c'))
    inner = outer[1]
    assert inner.index_in_parent == 1
    assert callable(inner.index)
    assert inner.index(pf.MetaString('c')) == 1
    with pytest.raises(AttributeError):
        inner.index = 0  # a method of the class, not the index_in_parent


def test_navigation_in_metalists():
    ml = pf.MetaList('a', pf.MetaList('b', 'c'), True)
    a, inner, last = ml[0], ml[1], ml[2]
    assert a.next is inner and inner.next is last and last.next is None
    assert inner.prev is a and a.prev is None
    assert a.offset(2) is last and last.offset(-2) is a
    assert inner.container is ml.content and inner.parent is ml
    b, c = inner[0], inner[1]
    assert b.next is c and c.prev is b and b.prev is None
    assert b.ancestor(2) is ml
    meta = pf.Doc(metadata={'list': ['x', ['y', 'z']]}).metadata
    nested = meta['list'][1]
    assert isinstance(nested, pf.MetaList) and nested.index_in_parent == 1
    assert nested.prev == pf.MetaString('x') and nested.next is None
    assert nested[1].prev == pf.MetaString('y')


# ---------------------------------------------------------------------------
# walk
# ---------------------------------------------------------------------------

def strs_in(elem):
    found = []
    elem.walk(lambda e, doc: found.append(e.text) if isinstance(e, pf.Str) else None)
    return found


def test_walk_returns_self_when_action_returns_none():
    doc = build_doc()
    assert doc.walk(lambda e, d: None) is doc
    para = doc.content[0]
    assert para.walk(lambda e, d: None) is para


def test_walk_visits_children_before_parents_in_document_order():
    doc = build_doc()
    tags = []
    doc.walk(lambda e, d: tags.append(e.tag))
    assert tags == ['Str', 'MetaInlines', 'MetaMap',
                    'Str', 'Space', 'Str', 'Emph', 'Str', 'Para',
                    'Str', 'Plain', 'Div',
                    'Str', 'Plain', 'ListItem', 'Str', 'Plain', 'ListItem', 'BulletList',
                    'Doc']


def test_walk_passes_doc():
    doc = build_doc()
    seen = set()
    doc.walk(lambda e, d: seen.add(id(d)))
    assert seen == {id(doc)}
    # An explicit doc is passed through as is
    other = pf.Doc()
    seen.clear()
    doc.content[0].walk(lambda e, d: seen.add(id(d)), doc=other)
    assert seen == {id(other)}
    # Without a Doc root, doc is None
    seen.clear()
    pf.Para(pf.Str('x')).walk(lambda e, d: seen.add(d))
    assert seen == {None}


def test_walk_replace_with_element():
    doc = pf.Doc(pf.Para(pf.Str('a'), pf.Space, pf.Str('b')))
    doc.walk(lambda e, d: pf.Str(e.text.upper()) if isinstance(e, pf.Str) else None)
    assert strs_in(doc) == ['A', 'B']
    doc.walk(lambda e, d: pf.CodeBlock('code') if isinstance(e, pf.Para) else None)
    assert to_json_value(doc)['blocks'] == [{'t': 'CodeBlock', 'c': [['', [], []], 'code']}]


def test_walk_replace_with_list():
    doc = pf.Doc(pf.Para(pf.Str('a')))
    doc.walk(lambda e, d: [pf.Str('x'), pf.Space, pf.Str('y')] if isinstance(e, pf.Str) else None)
    assert to_json_value(doc.content[0]) == {'t': 'Para', 'c': [
        {'t': 'Str', 'c': 'x'}, {'t': 'Space'}, {'t': 'Str', 'c': 'y'}]}
    doc.walk(lambda e, d: [pf.Para(pf.Str('1')), pf.Para(pf.Str('2'))] if isinstance(e, pf.Para) else None)
    assert strs_in(doc) == ['1', '2']


def test_walk_delete_with_empty_list():
    doc = pf.Doc(pf.Para(pf.Str('a'), pf.Space), pf.Para(pf.Str('b')),
                 metadata={'keep': 'x', 'drop': 'y'})
    doc.walk(lambda e, d: [] if isinstance(e, pf.Str) else None)
    assert to_json_value(doc)['blocks'] == [{'t': 'Para', 'c': [{'t': 'Space'}]}, {'t': 'Para', 'c': []}]
    doc.walk(lambda e, d: [] if isinstance(e, pf.Para) and not e.content else None)
    assert len(doc.content) == 1
    doc.walk(lambda e, d: [] if isinstance(e, pf.MetaString) and e.text == 'y' else None)
    assert list(doc.metadata) == ['keep']


def test_walk_action_return_value_for_root():
    para = pf.Para(pf.Str('a'))
    assert para.walk(lambda e, d: [] if isinstance(e, pf.Para) else None) == []
    replacement = pf.Plain()
    assert para.walk(lambda e, d: replacement if isinstance(e, pf.Para) else None) is replacement


def test_walk_wrong_replacement_type_raises():
    doc = pf.Doc(pf.Para(pf.Str('a')))
    with pytest.raises(TypeError):
        doc.walk(lambda e, d: pf.Para() if isinstance(e, pf.Str) else None)


def test_walk_replacement_is_not_walked_again():
    doc = pf.Doc(pf.Para(pf.Str('a')))
    calls = []

    def action(elem, d):
        calls.append(elem.tag)
        if isinstance(elem, pf.Para):
            return pf.Para(pf.Emph(pf.Str('new')))
    doc.walk(action)
    assert calls == ['MetaMap', 'Str', 'Para', 'Doc']
    assert strs_in(doc) == ['new']


def test_walk_mutating_in_place():
    doc = pf.Doc(pf.Header(pf.Str('h'), level=1))

    def action(elem, d):
        if isinstance(elem, pf.Header):
            elem.level += 1
    doc.walk(action)
    assert doc.content[0].level == 2


def test_walk_leaves_new_containers_with_the_same_elements():
    # After a walk, each parent holds a new container (the items are the
    # same objects, attached to it)
    doc = build_doc()
    para = doc.content[0]
    old_content, old_metadata = para.content, doc.metadata
    items = list(old_content)
    doc.walk(lambda e, d: None)
    assert para.content is not old_content and doc.metadata is not old_metadata
    assert all(x is y for x, y in zip(para.content.list, items))
    assert [(e.parent, e.location, e.index) for e in para.content.list] == [(para, None, i) for i in range(4)]


def test_walk_what_the_action_sees():
    # The action sees each element as part of the container being walked:
    # siblings after a replaced element keep their index until the walk of
    # the container is over
    para = pf.Para(pf.Emph(pf.Str('a')), pf.Str('b'), pf.Str('c'))
    cite = pf.Cite(pf.Str('x'), citations=[pf.Citation('id', prefix=[pf.Str('p')])])
    doc = pf.Doc(para, pf.Plain(cite))
    seen = []

    def action(elem, d):
        if isinstance(elem, pf.Str):
            seen.append((elem.text, type(elem.parent).__name__, elem.location, elem.index,
                         elem.prev.tag if elem.prev else None, elem.next.tag if elem.next else None))
        if isinstance(elem, pf.Emph):
            return [pf.Str('a1'), pf.Str('a2')]
    doc.walk(action)
    assert seen == [
        ('a', 'Emph', None, 0, None, None),
        ('b', 'Para', None, 1, 'Emph', 'Str'),
        ('c', 'Para', None, 2, 'Str', None),
        ('x', 'Cite', None, 0, None, None),
        ('p', 'Citation', 'prefix', 0, None, None),
    ]
    assert [(e.text, e.index) for e in para.content] == [('a1', 0), ('a2', 1), ('b', 2), ('c', 3)]


def test_walk_sees_changes_made_to_the_container_being_walked():
    # Filters can insert or delete siblings of the element they receive:
    # inserted elements after it are walked, deleted ones are not
    para = pf.Para(*[pf.Str(t) for t in ('a', 'b', 'c', 'd')])
    seen = []

    def action(elem, d):
        if isinstance(elem, pf.Str):
            seen.append((elem.text, elem.index))
            if elem.text == 'a':
                elem.parent.content.insert(elem.index + 1, pf.Str('new'))
            elif elem.text == 'b':
                del elem.parent.content[elem.index + 1]  # c
    pf.Doc(para).walk(action)
    assert seen == [('a', 0), ('new', 1), ('b', 2), ('d', 3)]
    assert [e.text for e in para.content] == ['a', 'new', 'b', 'd']


def test_walk_deemph_pattern():
    # As in examples/panflute/deemph.py: move the contents of an element
    # after it in its parent, and delete it
    para = pf.Para(pf.Str('x'), pf.Emph(pf.Str('a'), pf.Space, pf.Str('b')), pf.Str('y'))
    seen = []

    def action(elem, d):
        seen.append(elem.tag)
        if isinstance(elem, pf.Emph):
            for i, item in enumerate(elem.content, elem.index + 1):
                elem.parent.content.insert(i, item)
            return []
    pf.Doc(para).walk(action)
    assert [stringify_inline(e) for e in para.content] == ['x', 'a', ' ', 'b', 'y']
    # the moved elements are walked again, in their new place
    assert seen == ['MetaMap', 'Str', 'Str', 'Space', 'Str', 'Emph', 'Str', 'Space', 'Str', 'Str',
                    'Para', 'Doc']


def test_walk_wrong_replacement_type_raises_after_walking_the_siblings():
    para = pf.Para(pf.Str('a'), pf.Str('b'))
    seen = []

    def action(elem, d):
        seen.append(elem.tag)
        if isinstance(elem, pf.Str) and elem.text == 'a':
            return pf.Para()
    with pytest.raises(TypeError, match='Element "Panflute" received "Para"'):
        pf.Doc(para).walk(action)
    assert seen == ['MetaMap', 'Str', 'Str']
    assert [e.text for e in para.content] == ['a', 'b']  # unchanged


def test_walk_slice_does_not_attach():
    para = pf.Para(*[pf.Str(t) for t in ('a', 'b', 'c')])
    sl = para.content[1:]
    seen = []
    result = sl.walk(lambda e, d: seen.append((e.text, e.parent is para, e.index)))
    assert seen == [('b', True, 1), ('c', True, 2)]
    assert [e.text for e in result] == ['b', 'c']


def test_walk_stop_if():
    doc = build_doc()
    visited = []
    doc.walk(lambda e, d: visited.append(e.tag), stop_if=lambda e: isinstance(e, (pf.Emph, pf.Div)))
    # stopped elements are themselves visited, their children are not
    assert 'Emph' in visited and 'Div' in visited
    assert 'Plain' in visited  # (from the bullet list)
    assert visited.count('Str') == 5  # t, a, c, e, f (not b and d)
    stopped_strs = []
    doc.walk(lambda e, d: stopped_strs.append(e.text) if isinstance(e, pf.Str) else None,
             stop_if=lambda e: isinstance(e, pf.Doc))
    assert stopped_strs == []


def test_walk_children_attribute_set_on_all_elements():
    # walk relies on _children naming every attribute that holds elements
    expected = {
        'Doc': ['metadata', 'content'], 'Cite': ['content', 'citations'],
        'Citation': ['prefix', 'suffix'], 'DefinitionItem': ['term', 'definitions'],
        'Figure': ['content', 'caption'], 'Table': ['head', 'content', 'foot', 'caption'],
        'TableBody': ['content', 'head'], 'Caption': ['content', 'short_caption'],
        'Str': [], 'Space': [], 'Code': [], 'Math': [], 'MetaString': [], 'MetaBool': [],
    }
    for name, children in expected.items():
        assert getattr(pf, name)._children == children, name


def test_walk_through_table_parts():
    table = pf.Table(
        pf.TableBody(pf.TableRow(pf.TableCell(pf.Plain(pf.Str('b')))),
                     head=[pf.TableRow(pf.TableCell(pf.Plain(pf.Str('ih'))))]),
        head=pf.TableHead(pf.TableRow(pf.TableCell(pf.Plain(pf.Str('h'))))),
        foot=pf.TableFoot(pf.TableRow(pf.TableCell(pf.Plain(pf.Str('f'))))),
        caption=pf.Caption(pf.Plain(pf.Str('c')), short_caption=[pf.Str('s')]))
    table.walk(lambda e, d: pf.Str(e.text * 2) if isinstance(e, pf.Str) else None)
    assert strs_in(table) == ['hh', 'bb', 'ihih', 'ff', 'cc', 'ss']


# ---------------------------------------------------------------------------
# run_filters (as used by filters on an existing Doc)
# ---------------------------------------------------------------------------

def test_run_filters_sequence_prepare_finalize_and_kwargs():
    doc = build_doc()
    events = []

    def prepare(d):
        events.append('prepare')
        d.count = 0

    def count(elem, d, step):
        if isinstance(elem, pf.Str):
            d.count += step

    def upper(elem, d, step):
        if isinstance(elem, pf.Str):
            return pf.Str(elem.text.upper())

    def finalize(d):
        events.append(('finalize', d.count))

    result = pf.run_filters([count, upper], prepare=prepare, finalize=finalize, doc=doc, step=2)
    assert result is doc
    assert events == ['prepare', ('finalize', 14)]
    assert strs_in(doc) == ['T', 'A', 'B', 'C', 'D', 'E', 'F']


def test_run_filter_stop_if_and_wrapper():
    doc = build_doc()
    result = pf.run_filter(lambda e, d: pf.Str('x') if isinstance(e, pf.Str) else None,
                           doc=doc, stop_if=lambda e: isinstance(e, pf.Para))
    assert result is doc
    assert strs_in(doc) == ['x', 'a', 'b', 'c', 'x', 'x', 'x']


def test_run_filters_can_replace_the_doc():
    new = pf.Doc(pf.Para(pf.Str('new')))
    result = pf.run_filter(lambda e, d: new if isinstance(e, pf.Doc) else None, doc=build_doc())
    assert result is new


# ---------------------------------------------------------------------------
# replace_keyword
# ---------------------------------------------------------------------------

def test_replace_keyword_inline():
    p1 = pf.Para(pf.Str('Spam'), pf.Space, pf.Emph(pf.Str('and'), pf.Space, pf.Str('eggs')))
    p2 = pf.Para(pf.Str('eggs'))
    p3 = pf.Plain(pf.Emph(pf.Str('eggs')))
    doc = pf.Doc(p1, p2, p3)
    doc.replace_keyword('eggs', pf.Str('ham'))
    assert repr(doc.content) == ('ListContainer(Para(Str(Spam) Space Emph(Str(and) Space Str(ham))) '
                                 'Para(Str(ham)) Plain(Emph(Str(ham))))')
    assert doc.num_matches == 3


def test_replace_keyword_block():
    p1 = pf.Para(pf.Str('Spam'), pf.Space, pf.Emph(pf.Str('and'), pf.Space, pf.Str('ham')))
    doc = pf.Doc(p1, pf.Para(pf.Str('ham')), pf.Plain(pf.Emph(pf.Str('ham'))))
    doc.replace_keyword(keyword='ham', replacement=pf.Para(pf.Str('spam')))
    assert repr(doc.content) == ('ListContainer(Para(Str(Spam) Space Emph(Str(and) Space Str(ham))) '
                                 'Para(Str(spam)) Para(Str(spam)))')


def test_replace_keyword_count():
    doc = pf.Doc(pf.Para(pf.Str('x'), pf.Space, pf.Str('x'), pf.Space, pf.Str('x')))
    doc.replace_keyword('x', pf.Str('y'), count=2)
    assert strs_in(doc) == ['y', 'y', 'x']


def test_replace_keyword_on_subtree_and_errors():
    doc = pf.Doc(pf.Para(pf.Str('k')), pf.Para(pf.Str('k')))
    doc.content[0].replace_keyword('k', pf.Str('z'))
    assert strs_in(doc) == ['z', 'k']
    with pytest.raises(Exception, match='No root document'):
        pf.Para(pf.Str('k')).replace_keyword('k', pf.Str('z'))
    with pytest.raises(NotImplementedError):
        doc.replace_keyword('k', pf.MetaString('z'))


def test_replace_keyword_block_through_inline_wrapper():
    # An Inline holding only the keyword collapses to Str(keyword), so that its
    # parent block can then be replaced
    doc = pf.Doc(pf.Para(pf.Emph(pf.Str('k'))), pf.Para(pf.Str('k'), pf.Space),
                 pf.Para(pf.Str('k')), metadata={'m': pf.MetaInlines(pf.Str('k'))})
    doc.replace_keyword('k', pf.CodeBlock('X'), count=1)
    assert [b.tag for b in doc.content] == ['CodeBlock', 'Para', 'Para']
    assert repr(doc.content[2]) == 'Para(Str(k))'
    assert doc.get_metadata('m') == 'k'  # metadata is never replaced by blocks
