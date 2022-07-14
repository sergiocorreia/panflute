import panflute as pf


def validate(markdown_text, expected_text, verbose=False):
	doc = pf.convert_text(markdown_text, input_format='markdown', output_format='panflute', standalone=True)
	output_text = pf.stringify(doc)
	if verbose:
		print('<<<< EXPECTED <<<<')
		print(expected_text)
		print('<<<< OUTPUT <<<<')
		print(output_text)
		print('>>>>>>>>>>>>>>>>')
	assert expected_text == output_text


def test_simple():
	markdown_text = '''Hello **world**! *How* are ~you~ doing?'''
	expected_text = '''Hello world! How are you doing?\n\n'''
	validate(markdown_text, expected_text)


def test_cite():
	markdown_text = '[@abc, p.23]'
	expected_text = '[@abc, p.23]\n\n'
	validate(markdown_text, expected_text)


def test_definition_list():
	markdown_text = '''Term 1\n:   Definition 1\n\nTerm 2 with *inline markup*\n\n:   Definition 2'''
	expected_text = '''- Term 1: Definition 1\n- Term 2 with inline markup: Definition 2\n\n'''
	validate(markdown_text, expected_text)


def test_definition_list_complex():
	markdown_text = '''Term 1\n~ Definition 1\n\nTerm 2\n~ Definition 2a\n~ Definition 2b'''
	expected_text = '''- Term 1: Definition 1\n- Term 2: Definition 2a; Definition 2b'''
	validate(markdown_text, expected_text)


if __name__ == "__main__":
    test_simple()
    test_cite()
    test_definition_list()
    test_definition_list_complex()
