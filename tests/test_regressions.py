import io
import panflute as pf

def test_all():
    x=pf.Para(pf.Str("a"))
    y=pf.Para(pf.Str("b"))
    c1=pf.TableCell(x)
    c2=pf.TableCell(y)
    row=pf.TableRow(c1,c2)
    t1 = pf.Table(row)
    t2 = pf.Table(row, header=row)

    print(t1.header)
    print(t2.header)

    with io.StringIO() as f:
        pf.dump(pf.Doc(t1), f)
        print(f.getvalue())

    with io.StringIO() as f:
        pf.dump(pf.Doc(t2), f)
        print(f.getvalue())

def test_quotes_129():
    #pf https://github.com/sergiocorreia/panflute/issues/129
    text = [pf.Str("Some"), pf.Space, pf.Str("quoted text")]
    quoted_text = pf.Quoted(*text)
    para = pf.Para(quoted_text)
    output = pf.stringify(para, False)
    assert output == '"Some quoted text"'


if __name__ == "__main__":
    test_all()
    test_quotes_129()
