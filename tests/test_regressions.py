import io
import panflute as pf


def test_quotes_129():
    #pf https://github.com/sergiocorreia/panflute/issues/129
    text = [pf.Str("Some"), pf.Space, pf.Str("quoted text")]
    quoted_text = pf.Quoted(*text)
    para = pf.Para(quoted_text)
    output = pf.stringify(para, False)
    assert output == '"Some quoted text"'


if __name__ == "__main__":
    test_quotes_129()
