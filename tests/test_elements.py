import pytest

from panflute.elements import builtin2meta, MetaList, MetaMap, MetaString


class My_List(list):
    """Subclass for testing https://github.com/sergiocorreia/panflute/issues/166"""
    pass


class My_Dict(dict):
    """Subclass for testing https://github.com/sergiocorreia/panflute/issues/166"""
    pass


@pytest.mark.parametrize(
    "value,expected",
    [
        ([], MetaList()),
        ({}, MetaMap()),
        (My_List(), MetaList()),
        (My_Dict(), MetaMap()),
        (1, MetaString('1')),
        ('a', MetaString('a')),
        ([1], MetaList(MetaString('1'))),
        ({'a': My_List()}, MetaMap(a=MetaList())),
    ]
)
def test_builtin2meta(value, expected):
    assert builtin2meta(value) == expected
