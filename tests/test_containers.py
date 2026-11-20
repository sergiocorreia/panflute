"""
Tests for ListContainer and DictContainer: parent/location/index tracking,
slicing, insertion/deletion/assignment, and oktypes enforcement.
"""

import pytest

import panflute as pf
from panflute.containers import attach, to_json_wrapper


def strs(*texts):
    return [pf.Str(t) for t in texts]


def texts(container):
    return [e.text for e in container]


# ---------------------------------------------------------------------------
# ListContainer
# ---------------------------------------------------------------------------

def test_listcontainer_basic_sequence_protocol():
    lc = pf.ListContainer(*strs('a', 'b', 'c'), oktypes=pf.Str)
    assert len(lc) == 3
    assert texts(lc) == ['a', 'b', 'c']
    assert lc[0].text == 'a' and lc[-1].text == 'c'
    assert pf.Str('b') in lc
    assert pf.Str('z') not in lc
    assert lc.index(pf.Str('b')) == 1
    assert lc.count(pf.Str('a')) == 1
    assert texts(reversed(lc)) == ['c', 'b', 'a']
    with pytest.raises(IndexError):
        lc[3]
    assert lc.oktypes is pf.Str
    assert lc.parent is None and lc.location is None


def test_listcontainer_parent_and_index_on_construction():
    para = pf.Para(*strs('a', 'b'))
    lc = para.content
    assert lc.parent is para
    assert lc.location is None
    for i, item in enumerate(lc.list):
        assert item.parent is para
        assert item.index == i
        assert item.location is None


def test_listcontainer_getitem_attaches():
    para = pf.Para(*strs('a', 'b'))
    item = para.content.list[1]
    item.parent = item.index = None
    assert para.content[1] is item
    assert item.parent is para and item.index == 1
    # (negative indexes: see test_regressions.py::test_navigation_after_negative_indexing)


def test_listcontainer_location_is_propagated():
    cite = pf.Cite(citations=[pf.Citation('a'), pf.Citation('b')])
    assert cite.citations.location == 'citations'
    c = cite.citations[1]
    assert (c.parent, c.location, c.index) == (cite, 'citations', 1)
    cit = pf.Citation('x', prefix=strs('p'), suffix=strs('s'))
    assert cit.prefix[0].location == 'prefix'
    assert cit.suffix[0].location == 'suffix'


def test_listcontainer_slicing_returns_container():
    para = pf.Para(*strs('a', 'b', 'c', 'd'))
    sl = para.content[1:3]
    assert isinstance(sl, pf.ListContainer)
    assert texts(sl) == ['b', 'c']
    assert sl.parent is para
    assert sl.oktypes is para.content.oktypes
    assert texts(para.content[::-1]) == ['d', 'c', 'b', 'a']
    assert texts(para.content[::2]) == ['a', 'c']
    # the slice is a new container: changing it does not change the original
    sl.append(pf.Str('x'))
    assert len(para.content) == 4
    cit = pf.Citation('x', prefix=strs('a', 'b'))
    assert cit.prefix[0:1].location == 'prefix'


def test_listcontainer_insert_append_extend():
    para = pf.Para(pf.Str('b'))
    para.content.insert(0, pf.Str('a'))
    para.content.append(pf.Str('c'))
    para.content.extend([pf.Space, pf.Str('d')])
    assert [e.tag for e in para.content] == ['Str', 'Str', 'Str', 'Space', 'Str']
    assert texts(para.content[:3]) == ['a', 'b', 'c']
    new = para.content.list[0]
    assert new.parent is para and new.index == 0
    last = para.content.list[-1]
    assert last.parent is para and last.index == 4
    para.content += [pf.Str('e')]
    assert para.content[-1].text == 'e'


def test_listcontainer_setitem():
    para = pf.Para(*strs('a', 'b'))
    new = pf.Str('B')
    para.content[1] = new
    assert texts(para.content) == ['a', 'B']
    assert new.parent is para and new.index == 1
    para.content[0] = pf.Space  # class is instantiated
    assert isinstance(para.content[0], pf.Space)
    with pytest.raises(TypeError):
        para.content[0] = pf.Para()
    assert isinstance(para.content[0], pf.Space)


def test_listcontainer_delete_and_pop_and_remove():
    para = pf.Para(*strs('a', 'b', 'c', 'd'))
    del para.content[0]
    assert texts(para.content) == ['b', 'c', 'd']
    del para.content[0:2]
    assert texts(para.content) == ['d']
    para.content.extend(strs('e', 'f'))
    assert para.content.pop().text == 'f'
    para.content.remove(pf.Str('d'))
    assert texts(para.content) == ['e']
    para.content.clear()
    assert len(para.content) == 0


def test_listcontainer_reverse_and_iadd():
    para = pf.Para(*strs('a', 'b', 'c'))
    para.content.reverse()
    assert texts(para.content) == ['c', 'b', 'a']
    assert [e.index for e in para.content] == [0, 1, 2]


def test_listcontainer_oktypes_enforced_everywhere():
    para = pf.Para()
    bad = pf.Para()
    for op in (lambda: para.content.append(bad),
               lambda: para.content.insert(0, bad),
               lambda: para.content.extend([bad]),
               lambda: para.content.__setitem__(0, bad),
               lambda: pf.ListContainer(bad, oktypes=pf.Inline),
               lambda: pf.ListContainer('text', oktypes=pf.Inline)):
        with pytest.raises(TypeError):
            op()
    assert len(para.content) == 0
    lc = pf.ListContainer(pf.Str('a'), pf.Para(), oktypes=(pf.Str, pf.Para))
    assert len(lc) == 2
    assert len(pf.ListContainer(1, 'x', oktypes=object)) == 2


def test_listcontainer_equality():
    a = pf.Para(*strs('a', 'b')).content
    b = pf.Para(*strs('a', 'b')).content
    c = pf.Para(*strs('a')).content
    assert a == b
    assert a != c
    assert pf.Para(pf.Str('a')).content != pf.Para(pf.Str('b')).content
    # oktypes and location are part of equality, the parent is not
    assert pf.Para(pf.Str('a')).content != pf.Div().content
    assert pf.Citation('x', prefix=strs('a')).prefix != pf.Citation('x', suffix=strs('a')).suffix
    assert pf.Para(pf.Str('a')).content == pf.Plain(pf.Str('a')).content


def test_listcontainer_repr_and_to_json():
    lc = pf.Para(pf.Str('a'), pf.Space).content
    assert repr(lc) == str(lc) == 'ListContainer(Str(a) Space)'
    assert lc.to_json() == [{'t': 'Str', 'c': 'a'}, {'t': 'Space'}]


def test_listcontainer_walk_flattens_lists():
    para = pf.Para(*strs('a', 'b', 'c'))

    def action(elem, doc):
        if isinstance(elem, pf.Str):
            if elem.text == 'a':
                return []
            if elem.text == 'b':
                return [pf.Str('b1'), pf.Str('b2')]
    result = para.content.walk(action)
    assert isinstance(result, list)
    assert [e.text for e in result] == ['b1', 'b2', 'c']


# ---------------------------------------------------------------------------
# DictContainer
# ---------------------------------------------------------------------------

def test_dictcontainer_mapping_protocol():
    dc = pf.DictContainer(('a', pf.MetaString('x')), b=pf.MetaBool(True), oktypes=pf.MetaValue)
    assert len(dc) == 2
    assert list(dc) == ['a', 'b']
    assert 'a' in dc and 'z' not in dc
    assert dc['a'] == pf.MetaString('x')
    assert dict(dc) == {'a': pf.MetaString('x'), 'b': pf.MetaBool(True)}
    dc['c'] = pf.MetaString('y')
    del dc['a']
    assert list(dc.keys()) == ['b', 'c']
    assert dc.get('a') is None
    with pytest.raises(KeyError):
        dc['a']
    with pytest.raises(TypeError):
        dc['d'] = pf.Str('x')
    with pytest.raises(TypeError):
        pf.DictContainer(('k', 'not meta'), oktypes=pf.MetaValue)
    assert repr(dc) == str(dc) == "DictContainer('b' 'c')"
    assert dc.to_json() == {'b': {'t': 'MetaBool', 'c': True}, 'c': {'t': 'MetaString', 'c': 'y'}}


def test_dictcontainer_parent_tracking():
    mm = pf.MetaMap(a=pf.MetaString('x'))
    value = mm.content.dict['a']
    assert value.parent is mm
    assert value.location is None and value.index is None
    new = pf.MetaString('y')
    mm.content['b'] = new
    assert new.parent is mm
    doc = pf.Doc(metadata={'k': 'v'})
    assert doc.metadata['k'].parent is doc.metadata
    assert doc.metadata.parent is doc
    assert doc.metadata['k'].doc is doc


def test_dictcontainer_equality():
    a = pf.MetaMap(a='x').content
    assert a == pf.MetaMap(a='x').content
    assert a != pf.MetaMap(a='y').content


def test_dictcontainer_walk_drops_deleted_items():
    mm = pf.MetaMap(a='x', b='y')

    def action(elem, doc):
        if isinstance(elem, pf.MetaString) and elem.text == 'x':
            return []
    result = mm.content.walk(action)
    assert result == [('b', pf.MetaString('y'))]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def test_attach_ignores_builtins():
    parent = pf.Para()
    for value in (1, 'x', True):
        assert attach(value, parent, None, 0) == value
    s = pf.Str('a')
    assert attach(s, parent, 'loc', 3) is s
    assert (s.parent, s.location, s.index) == (parent, 'loc', 3)


def test_to_json_wrapper():
    assert to_json_wrapper('x') == 'x'
    assert to_json_wrapper(True) == {'t': 'MetaBool', 'c': True}
    assert to_json_wrapper(pf.Str('a')) == {'t': 'Str', 'c': 'a'}
