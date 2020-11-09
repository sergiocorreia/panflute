import panflute as pf
from pathlib import Path


def test():
    # chcp 65001 --> might be required if running from cmd on Windows

    fn = Path("./tests/sample_files/heavy_metadata/example.md")
    print(f'\n - Loading markdown "{fn}"')
    with fn.open(encoding='utf-8') as f:
        markdown_text = f.read()
    print(' - Converting Markdown to JSON')
    json_pandoc = pf.convert_text(markdown_text, input_format='markdown', output_format='json', standalone=True)
    print(' - Constructing Doc() object')
    doc = pf.convert_text(json_pandoc, input_format='json', output_format='panflute', standalone=True)

    print(' - Verifying that we can access metadata correctly')
    
    meta = doc.get_metadata('title')
    assert meta == "Lorem Ipsum: Title"
    
    meta = doc.get_metadata('title', builtin=False)
    assert type(meta) == pf.MetaInlines

    # foobar key doesn't exist
    meta = doc.get_metadata('foobar', True)
    assert meta == True

    meta = doc.get_metadata('foobar', 123)
    assert meta == 123

    meta = doc.get_metadata('abstract')
    assert meta.startswith('Bring to the table win-win')

    meta = doc.get_metadata('key1.key1-1')
    assert meta == ['value1-1-1', 'value1-1-2']

    meta = doc.get_metadata('amsthm.plain')
    assert type(meta) == list
    assert meta[0]['Theorem'] == 'Lemma'

    meta = doc.get_metadata('')
    assert len(meta) > 10

    print(' - Done!')

if __name__ == "__main__":
    test()
