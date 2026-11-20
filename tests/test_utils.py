"""
Tests for panflute.utils (helpers with no dependencies on the rest of panflute).
"""

import sys

import pytest

import panflute as pf
from panflute.utils import (
    ContextImport, check_group, check_type, check_type_or_value, decode_ica, encode_dict,
    get_caller_name, load_pandoc_reader_options, load_pandoc_version)

from .helpers import FIXTURES

pytestmark = pytest.mark.usefixtures('clean_import_state')


def test_context_import_file_path():
    test_file = str(FIXTURES / 'dependency' / 'dependency.py')
    path_before = list(sys.path)
    with ContextImport(test_file) as module:
        assert sys.path[0] == str(FIXTURES / 'dependency')
        assert module.test_function() is True
        assert module.test_class().test_me() == "I'm a test"
    assert sys.path == path_before


def test_context_import_module_with_extra_dir():
    path_before = list(sys.path)
    with ContextImport('foo.test_filter', str(FIXTURES / 'panfl')) as module:
        assert module.__name__ == 'foo.test_filter'
        assert callable(module.main)
    assert sys.path == path_before
    ci = ContextImport('dependency.py', None)
    assert (ci.module, ci.extra_dir) == ('dependency', None)
    ci = ContextImport('/some/dir/mod.py')
    assert (ci.module, ci.extra_dir) == ('mod', '/some/dir')


def test_context_import_module_already_on_path():
    path_before = list(sys.path)
    with ContextImport('json') as module:
        assert sys.path == path_before
        assert module.loads('[1]') == [1]
    assert sys.path == path_before


def test_context_import_missing_module():
    # (sys.path handling on failure: see test_regressions.py)
    with pytest.raises(ImportError):
        with ContextImport('panflute_no_such_module_xyz', str(FIXTURES)):
            pass


def test_check_type():
    assert check_type('x', str) == 'x'
    assert check_type(1, (int, float)) == 1
    space = check_type(pf.Space, pf.Inline)
    assert isinstance(space, pf.Space)
    with pytest.raises(TypeError, match='received "int" but expected'):
        check_type(1, str)


def test_check_group():
    assert check_group('a', {'a', 'b'}) == 'a'
    with pytest.raises(TypeError, match='element str not in group'):
        check_group('c', {'a', 'b'})


def test_check_type_or_value():
    assert check_type_or_value(0.5, (float, int), 'ColWidthDefault') == 0.5
    assert check_type_or_value('ColWidthDefault', (float, int), 'ColWidthDefault') == 'ColWidthDefault'
    with pytest.raises(TypeError, match='or ColWidthDefault'):
        check_type_or_value('other', (float, int), 'ColWidthDefault')


def test_get_caller_name():
    # get_caller_name() reports the class of the closest __init__ frame above
    # its caller, skipping container classes
    class Outer:
        def __init__(self):
            self.name = (lambda: get_caller_name())()

    assert Outer().name == 'Outer'
    with pytest.raises(TypeError, match='Element "Para"'):
        pf.Para('not an inline')
    with pytest.raises(TypeError, match='Element "Citation"'):
        pf.Citation('id', prefix=['x'])


def test_encode_decode():
    assert encode_dict('Str', 'x') == {'t': 'Str', 'c': 'x'}
    assert decode_ica(['id', ['c'], [['k', 'v']]]) == {
        'identifier': 'id', 'classes': ['c'], 'attributes': [['k', 'v']]}


def test_load_pandoc_version(monkeypatch):
    monkeypatch.delenv('PANDOC_VERSION', raising=False)
    assert load_pandoc_version() is None
    monkeypatch.setenv('PANDOC_VERSION', '2.11.4')
    assert load_pandoc_version() == (2, 11, 4)
    monkeypatch.setenv('PANDOC_VERSION', '3.1')
    assert load_pandoc_version() == (3, 1)


def test_load_pandoc_reader_options(monkeypatch):
    monkeypatch.delenv('PANDOC_READER_OPTIONS', raising=False)
    assert load_pandoc_reader_options() == {}
    monkeypatch.setenv('PANDOC_READER_OPTIONS', '{"abbreviations": ["Mr."], "standalone": true}')
    assert load_pandoc_reader_options() == {'abbreviations': ['Mr.'], 'standalone': True}


def test_public_api_names():
    expected = {
        'debug', 'ListContainer', 'DictContainer', 'Element', 'Block', 'Inline', 'MetaValue',
        'Doc', 'Citation', 'ListItem', 'DefinitionItem', 'Definition', 'LineItem',
        'Null', 'HorizontalRule', 'Space', 'SoftBreak', 'LineBreak', 'Str', 'Code', 'BlockQuote',
        'Note', 'Div', 'Plain', 'Para', 'Emph', 'Strong', 'Underline', 'Strikeout', 'Superscript',
        'Subscript', 'SmallCaps', 'Span', 'RawBlock', 'RawInline', 'Math', 'CodeBlock', 'Link',
        'Image', 'BulletList', 'OrderedList', 'DefinitionList', 'LineBlock', 'Figure', 'Header',
        'Quoted', 'Cite', 'Table', 'TableHead', 'TableFoot', 'TableBody', 'TableRow', 'TableCell',
        'Caption', 'MetaList', 'MetaMap', 'MetaString', 'MetaBool', 'MetaInlines', 'MetaBlocks',
        'load', 'dump', 'run_filter', 'run_filters', 'toJSONFilter', 'toJSONFilters', 'stringify',
        'yaml_filter', 'shell', 'run_pandoc', 'convert_text', 'get_option', 'main', 'panfl',
        'get_filter_dirs', 'stdio', '__version__',
    }
    missing = {name for name in expected if not hasattr(pf, name)}
    assert not missing
    assert isinstance(pf.__version__, str) and pf.__version__[0].isdigit()
    assert callable(pf.Doc.get_metadata)
    assert callable(pf.Element.replace_keyword)
