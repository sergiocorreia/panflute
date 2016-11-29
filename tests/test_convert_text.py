import io
import panflute as pf

def test_all():
    md = 'Some *markdown* **text** ~xyz~'
    c_md = pf.convert_text(md)
    b_md = [pf.Para(pf.Str("Some"), pf.Space,
                    pf.Emph(pf.Str("markdown")), pf.Space,
                    pf.Strong(pf.Str("text")), pf.Space,
                    pf.Subscript(pf.Str("xyz")))]

    print("Benchmark MD:")
    print(b_md)
    print("Converted MD:")
    print(c_md)
    assert repr(c_md) == repr(b_md)

    with io.StringIO() as f:
        doc = pf.Doc(*c_md)
        pf.dump(doc, f)
        c_md_dump = f.getvalue()

    with io.StringIO() as f:
        doc = pf.Doc(*b_md)
        pf.dump(doc, f)
        b_md_dump = f.getvalue()

    assert c_md_dump == b_md_dump

    # ----------------------
    print()

    tex = r'Some $x^y$ or $x_n = \sqrt{a + b}$ \textit{a}'
    c_tex = pf.convert_text(tex)
    b_tex = [pf.Para(pf.Str("Some"), pf.Space,
                     pf.Math("x^y", format='InlineMath'), pf.Space,
                     pf.Str("or"), pf.Space,
                     pf.Math(r"x_n = \sqrt{a + b}", format='InlineMath'),
                     pf.Space, pf.RawInline(r"\textit{a}", format='tex'))]

    print("Benchmark TEX:")
    print(b_tex)
    print("Converted TEX:")
    print(c_tex)
    assert repr(c_tex) == repr(b_tex)

    with io.StringIO() as f:
        doc = pf.Doc(*c_tex)
        pf.dump(doc, f)
        c_tex_dump = f.getvalue()

    with io.StringIO() as f:
        doc = pf.Doc(*b_tex)
        pf.dump(doc, f)
        b_tex_dump = f.getvalue()

    assert c_tex_dump == b_tex_dump


    print("\nBack and forth conversions... md->json->md")
    md = 'Some *markdown* **text** ~xyz~'
    print("[MD]", md)
    md2json = pf.convert_text(md, input_format='markdown', output_format='json')
    print("[JSON]", md2json)
    md2json2md = pf.convert_text(md2json, input_format='json', output_format='markdown')
    print("[MD]", md2json2md)
    assert md == md2json2md


    print("\nBack and forth conversions... md->panflute->md")
    md = 'Some *markdown* **text** ~xyz~'
    print("[MD]", md)
    md2panflute = pf.convert_text(md, input_format='markdown', output_format='panflute')
    print("[PANFLUTE]", md2panflute)
    md2panflute2md = pf.convert_text(md2panflute, input_format='panflute', output_format='markdown')
    print("[MD]", md2panflute2md)
    assert md == md2panflute2md

    print("\nBack and forth conversions... md->panflute(standalone)->md")
    md = 'Some *markdown* **text** ~xyz~'
    print("[MD]", md)
    md2panflute = pf.convert_text(md, input_format='markdown', output_format='panflute', standalone=True)
    print("[PANFLUTE]", md2panflute)
    md2panflute2md = pf.convert_text(md2panflute, input_format='panflute', output_format='markdown')
    print("[MD]", md2panflute2md)
    assert md == md2panflute2md

    print("\nBack and forth conversions... md table -> json(standalone) -> md table")
    md = """  --- ---
  x   y
  --- ---

"""
    print("[MD]", repr(md))
    md2json = pf.convert_text(md, input_format='markdown', output_format='json', standalone=True)
    print("[json]", md2json)
    md2json2md = pf.convert_text(md2json, input_format='json', output_format='markdown')
    print("[MD]", repr(md2json2md))
    assert md == md2json2md


    print("\nBack and forth conversions... md table -> panflute(standalone) -> md table")
    print("[MD]", repr(md))
    md2panflute = pf.convert_text(md, input_format='markdown', output_format='panflute', standalone=True)
    print("[PANFLUTE]", md2panflute)
    md2panflute2md = pf.convert_text(md2panflute, input_format='panflute', output_format='markdown')
    print("[MD]", repr(md2panflute2md))
    assert md == md2panflute2md


if __name__ == "__main__":
    test_all()
