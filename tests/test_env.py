'''
Test that we are able to access environment vars set by Pandoc

See: https://pandoc.org/filters.html#environment-variables
'''

import panflute as pf
from pathlib import Path


def test_env():
	# A Doc() created by panflute has no environment vars
	print(f'\n - Testing Doc() created by panflute:')
	doc = pf.Doc()
	assert doc.pandoc_version is None
	assert isinstance(doc.pandoc_reader_options, dict) and not doc.pandoc_reader_options
	print(f' - No environment vars; as expected')

	# A Doc() created by running convert_text also doesn't
	print(f'\n - Testing Doc() created by panflute.convert_text():')
	fn = Path("./tests/sample_files/fenced/example.md")
	with fn.open(encoding='utf-8') as f:
	    markdown_text = f.read()
	json_pandoc = pf.convert_text(markdown_text, input_format='markdown', output_format='json', standalone=True)
	doc = pf.convert_text(json_pandoc, input_format='json', output_format='panflute', standalone=True)
	assert doc.pandoc_version is None
	assert isinstance(doc.pandoc_reader_options, dict) and not doc.pandoc_reader_options
	print(f' - No environment vars; as expected')

	print(f'\n - Testing Doc() as created by a filter:')
	pf.run_pandoc(text='Hello!', args=['--filter=./tests/filters/assert_env.py'])
	print(f' - Found environment vars; as expected')




if __name__ == "__main__":
    test_env()
