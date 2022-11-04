import io
import panflute as pf


def test_quotes_129():
    #pf https://github.com/sergiocorreia/panflute/issues/129
    text = [pf.Str("Some"), pf.Space, pf.Str("quoted text")]
    quoted_text = pf.Quoted(*text)
    para = pf.Para(quoted_text)
    output = pf.stringify(para, False)
    assert output == '"Some quoted text"'


def test_index_223():
    """Index values on duplicated elements are determined using list.index()
    but this returns the index first found element.
    This test checks whether the index on the element corresponds with the
    actual index in the parent collection.
    """
    # pf https://github.com/sergiocorreia/panflute/issues/223
    doc = pf.Doc(pf.Para(pf.Str("a")), pf.Para(pf.Str("b")),
                 pf.Para(pf.Str("a")), pf.Para(pf.Str("c")))

    for (index, element) in enumerate(doc.content):
        assert element.index == index


if __name__ == "__main__":
    test_quotes_129()
    test_index_223()
