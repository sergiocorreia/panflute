from panflute import Doc

def test_get_variable():
    doc = Doc(metadata={"a": 3, "b": {"c": 4}})
    assert get_variable(default="a") == "a"
    assert get_variable({"a": 1}, "a") == 1
    assert get_variable({"a": None}, "a", default=2) == 2
    assert get_variable({"a": None}, "a", doc, "a") == '3'
    assert get_variable(doc=doc, doc_tag="b.c") == '4'