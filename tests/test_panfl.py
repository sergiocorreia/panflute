"""
Tests for the -autofilter- option, where pandoc is called as:
> pandoc -F panf

And the metadata of the python file has the keys:
  panflute-filters  : a string or list
  panflute-path     : optional folder that contains filters

Additionally, there are two extra keys:
  panflute-verbose  : True to display debugging info
  panflute-echo     : Message to display on success
"""

# ---------------------------
# Imports
# ---------------------------


import os
import io
import sys
import subprocess
from pathlib import Path

import panflute as pf


# ---------------------------
# Setup
# ---------------------------

# Change path to the root panflute folder
os.chdir(str(Path(__file__).parents[1]))


# ---------------------------
# Tests
# ---------------------------

def test_get_filter_dirs():
    assert sorted(pf.get_filter_dirs()) == sorted(pf.get_filter_dirs(hardcoded=False))


def test_metadata():
    """
    panfl can receive filter lists either as a metadata argument or in the YAML block
    This tests that both work

    test_filter.py is a simple filter that edits a math expression by replacing "-" with "+"
    and attaching the document type (html, markdown, etc.)
    """

    def to_json(text):
        return pf.convert_text(text, 'markdown', 'json')

    def assert_equal(*extra_args, input_text, output_text):
        """
        Default values for extra_args:
        filters=None, search_dirs=None, data_dir=True, sys_path=True, panfl_=False
        """
        
        # Set --from=markdown
        sys.argv[1:] = []
        sys.argv.append('markdown')

        _stdout = io.StringIO()
        pf.stdio(*extra_args, input_stream=io.StringIO(input_text), output_stream=_stdout)
        _stdout = pf.convert_text(_stdout.getvalue(), 'json', 'markdown')
        assert _stdout == output_text

    md_contents = "$1-1$"
    md_document = """---
panflute-filters: test_filter
panflute-path: ./tests/test_panfl/bar
...
{}
""".format(md_contents)
    expected_output = '$1+1markdown$'

    json_contents = to_json(md_contents)
    json_document = to_json(md_document)

    # Filter in YAML block; try `panf_` true and false (this is a minor option that changes how the path gets built)
    assert_equal(None, None, True, True, True, input_text=json_document, output_text=expected_output)
    assert_equal(None, None, True, True, False, input_text=json_document, output_text=expected_output)

    # Open the filter as a standalone python script within a folder
    assert_equal(['test_filter.py'], ['./tests/test_panfl/bar'], True, True, False, input_text=json_contents, output_text=expected_output)

    # Open the filter with the exact abs. path (no need for folder)
    assert_equal([os.path.abspath('./tests/test_panfl/bar/test_filter.py')], [], False, True, True, input_text=json_contents, output_text=expected_output)

    # Open the filter as part of a package (packagename.module)
    assert_equal(['foo.test_filter'], ['./tests/test_panfl'], False, True, True, input_text=json_contents, output_text=expected_output)
    assert_equal(['test_filter'], ['./tests/test_panfl/foo'], False, True, True, input_text=json_contents, output_text=expected_output)


def test_pandoc_call():
    """
    This is a more difficult test as it also relies on Pandoc calling Panflute
    """

    def run_proc(*args, stdin):
        #assert not args, args
        proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=stdin, encoding='utf-8', cwd=os.getcwd())
        _stdout, _stderr = proc.stdout, proc.stderr
        return (_stdout if _stdout else '').strip(), (_stderr if _stderr else '').strip()

    md_contents = "$1-1$"
    expected_output = '$1+1markdown$'

    stdout = run_proc('pandoc', '--filter=panfl', '--to=markdown',
                      '--metadata=panflute-verbose:True',
                      '--metadata=panflute-filters:' + os.path.abspath('./tests/test_panfl/bar/test_filter.py'),
                      stdin=md_contents)[0]
    assert stdout == expected_output

    stdout = run_proc('pandoc', '--filter=panfl', '--to=markdown',
                      '--metadata=panflute-filters:test_filter',
                      '--metadata=panflute-path:./tests/test_panfl/bar',
                      stdin=md_contents)[0]
    assert stdout == expected_output


if __name__ == "__main__":
    test_get_filter_dirs()
    test_metadata()
    test_pandoc_call()