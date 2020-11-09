'''
Test that running panflute through a markdown file has no effect on the output

For each markdown test file, this runs:
a) pandoc --> json
b) json --> panflute --> json

And verifies that the outputs of a) and b) are the same
'''


import json
from pathlib import Path
import panflute as pf


def test_idempotence():
	example_files = list(Path('./tests/sample_files').glob('*/example.md'))
	print(f'Testing idempotence ({len(example_files)} files):')
	
	for fn in example_files:
		print(f'\n - Loading markdown "{fn}"')
		with fn.open(encoding='utf-8') as f:
			markdown_text = f.read()

		print(' - Converting markdown to JSON')
		json_pandoc = pf.convert_text(markdown_text, input_format='markdown', output_format='json', standalone=True)

		print(' - Constructing Doc() object')
		doc = pf.convert_text(json_pandoc, input_format='json', output_format='panflute', standalone=True)
		
		print(' - Converting Doc() to JSON...')
		json_panflute = pf.convert_text(doc, input_format='panflute', output_format='json', standalone=True)

		print(' - Are both JSON files equal?')
		print(f'    - Length: {len(json_pandoc) == len(json_panflute)} ({len(json_pandoc)} vs {len(json_panflute)})')
		print(f'    - Content: {json_pandoc == json_panflute}')
		assert json_pandoc == json_panflute

		print(' - Running filter that does nothing...')
		doc = doc.walk(action=empty_test, doc=doc)
		json_panflute = pf.convert_text(doc, input_format='panflute', output_format='json', standalone=True)
		print(' - Are both JSON files equal?')
		print(f'    - Length: {len(json_pandoc) == len(json_panflute)} ({len(json_pandoc)} vs {len(json_panflute)})')
		print(f'    - Content: {json_pandoc == json_panflute}')
		assert json_pandoc == json_panflute


def test_idempotence_of_native():
	example_files = list(Path('./tests/sample_files/native').glob('*.native'))
	print(f'Testing idempotence ({len(example_files)} native files):')
	
	for fn in example_files:
		print(f'\n - Loading native files "{fn}"')
		with fn.open(encoding='utf-8') as f:
			markdown_text = f.read()

		print(' - Converting native to JSON')
		json_pandoc = pf.convert_text(markdown_text, input_format='native', output_format='json', standalone=True)

		print(' - Constructing Doc() object')
		doc = pf.convert_text(json_pandoc, input_format='json', output_format='panflute', standalone=True)
		
		print(' - Converting Doc() to JSON...')
		json_panflute = pf.convert_text(doc, input_format='panflute', output_format='json', standalone=True)

		print(' - Are both JSON files equal?')
		print(f'    - Length: {len(json_pandoc) == len(json_panflute)} ({len(json_pandoc)} vs {len(json_panflute)})')
		print(f'    - Content: {json_pandoc == json_panflute}')
		assert json_pandoc == json_panflute

		print(' - Running filter that does nothing...')
		doc = doc.walk(action=empty_test, doc=doc)
		json_panflute = pf.convert_text(doc, input_format='panflute', output_format='json', standalone=True)
		print(' - Are both JSON files equal?')
		print(f'    - Length: {len(json_pandoc) == len(json_panflute)} ({len(json_pandoc)} vs {len(json_panflute)})')
		print(f'    - Content: {json_pandoc == json_panflute}')
		assert json_pandoc == json_panflute


def empty_test(element, doc):
    return


def test_stringify():
	markdown_text = '''Hello **world**! *How* are ~you~ doing?'''
	expected_text = '''Hello world! How are you doing?\n\n'''

	doc = pf.convert_text(markdown_text, input_format='markdown', output_format='panflute', standalone=True)
	output_text = pf.stringify(doc)

	assert expected_text == output_text



if __name__ == "__main__":
    test_idempotence_of_native()
    test_idempotence()
    test_stringify()
