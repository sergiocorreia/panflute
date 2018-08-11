import panflute as pf

def test_get_variable():
    
    doc = pf.Doc(metadata={"a": pf.MetaString("x"),
                           "b": pf.MetaMap(c=pf.MetaString("y"))})
    
    assert pf.get_option(default="a") == "a"
    assert pf.get_option({"a": 1}, "a") == 1
    assert pf.get_option({"a": None}, "a", default=2) == 2
    assert pf.get_option({"a": None}, "a", doc, "a") == "x"
    assert pf.get_option(doc=doc, doc_tag="b.c") == "y"
