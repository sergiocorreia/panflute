import pytest

from panflute.elements import builtin2meta, MetaList, MetaMap, MetaString


class My_List(list):
    """Subclass for testing https://github.com/sergiocorreia/panflute/issues/166"""
    pass


class My_Dict(dict):
    """Subclass for testing https://github.com/sergiocorreia/panflute/issues/166"""
    pass


class Not_Builtin:
    pass


@pytest.mark.parametrize(
    "value,expect_type",
    [
        ([], MetaList),
        ({}, MetaMap),
        (My_List(), MetaList),
        (My_Dict(), MetaMap),
        (1, MetaString),
        ('a', MetaString),
        ([1], MetaList),
        ({'a': My_List()}, MetaMap),
        (Not_Builtin(), Not_Builtin)
    ]
)
def test_builtin2meta(value, expect_type):
    """
    test output types of builtin2meta.
    Comparison of output value would be preferable,
    but does not work since __eq__ methods are not defined for MetaValue classes.
    """
    assert type(builtin2meta(value)) == expect_type
