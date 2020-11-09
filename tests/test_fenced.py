# To create the JSON file, run
# pandoc --smart --parse-raw --to=json fenced/input.md > fenced/input.json

import panflute as pf
from pathlib import Path


def fenced_action(options, data, element, doc):
    bar = options.get('foo')
    assert bar is None or bar == 'bar'
    assert not data or data == 'raw text' or \
        data == """raw1\nraw2\nthis\n...\nis\n...\nall raw"""
    # assert bar or data, (bar,data)
    return


def test_all():

    fn = Path("./tests/sample_files/fenced/example.md")
    print(f'\n - Loading markdown "{fn}"')
    with fn.open(encoding='utf-8') as f:
        markdown_text = f.read()
    print(' - Converting Markdown to JSON')
    json_pandoc = pf.convert_text(markdown_text, input_format='markdown', output_format='json', standalone=True)
    print(' - Constructing Doc() object')
    doc = pf.convert_text(json_pandoc, input_format='json', output_format='panflute', standalone=True)    

    print(' - Applying YAML filter...')
    pf.run_filter(pf.yaml_filter, tag='spam', function=fenced_action, doc=doc)
    json_panflute = pf.convert_text(doc, input_format='panflute', output_format='json', standalone=True)
    print('   Are both JSON files equal?')
    print(f'    - Length: {len(json_pandoc) == len(json_panflute)} ({len(json_pandoc)} vs {len(json_panflute)})')
    print(f'    - Content: {json_pandoc == json_panflute}')
    assert json_pandoc == json_panflute

    print(' - Applying Strict YAML filter...')
    pf.run_filter(pf.yaml_filter, tag='eggs', function=fenced_action, doc=doc, strict_yaml=True)
    json_panflute = pf.convert_text(doc, input_format='panflute', output_format='json', standalone=True)
    print('   Are both JSON files equal?')
    print(f'    - Length: {len(json_pandoc) == len(json_panflute)} ({len(json_pandoc)} vs {len(json_panflute)})')
    print(f'    - Content: {json_pandoc == json_panflute}')
    assert json_pandoc == json_panflute

    print(' - Done!')


if __name__ == "__main__":
    test_all()
