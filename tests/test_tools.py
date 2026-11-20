"""
Tests for panflute.tools: stringify, yaml_filter, metadata helpers,
get_option, convert_text, run_pandoc, shell, PandocVersion, and debug.
"""

import subprocess
import sys

import pytest
import yaml

import panflute as pf
import panflute.tools as tools
from panflute.tools import meta2builtin

from .helpers import JSON_FIXTURES, PANDOC, load_path


# ---------------------------------------------------------------------------
# stringify
# ---------------------------------------------------------------------------

def test_stringify_inlines():
    para = pf.Para(pf.Emph(pf.Str('Hello'), pf.Space, pf.Str('world!')), pf.Space, pf.Strong(pf.Str('Bye!')))
    assert pf.stringify(para) == 'Hello world! Bye!\n\n'
    assert pf.stringify(para, newlines=False) == 'Hello world! Bye!'
    assert pf.stringify(pf.Str('x')) == 'x'
    assert pf.stringify(pf.Plain(pf.Str('a'), pf.SoftBreak, pf.Str('b'), pf.LineBreak, pf.Str('c'))) == 'a b c'
    assert pf.stringify(pf.Plain(pf.Code('code'), pf.Math('x^2'), pf.RawInline('<b>'))) == 'codex^2<b>'
    assert pf.stringify(pf.Plain(pf.Link(pf.Str('text'), url='http://url'))) == 'text'
    assert pf.stringify(pf.Plain(pf.Image(pf.Str('alt'), url='a.png'))) == 'alt'
    assert pf.stringify(pf.Para()) == '\n\n'
    assert pf.stringify(pf.HorizontalRule()) == ''


def test_stringify_quoted():
    para = pf.Para(pf.Quoted(pf.Str('Some'), pf.Space, pf.Str('quoted text')))
    assert pf.stringify(para, False) == '"Some quoted text"'
    single = pf.Plain(pf.Quoted(pf.Str('x'), quote_type='SingleQuote'))
    assert pf.stringify(single) == '"x"'
    assert pf.stringify(pf.Plain(pf.Quoted())) == ''


def test_stringify_blocks():
    doc = pf.Doc(pf.Header(pf.Str('Title')), pf.Para(pf.Str('a')), pf.CodeBlock('code'),
                 pf.BulletList(pf.ListItem(pf.Plain(pf.Str('i1'))), pf.ListItem(pf.Para(pf.Str('i2')))))
    assert pf.stringify(doc) == 'Titlea\n\ncodei1i2\n\n'


def test_stringify_cite_uses_its_text():
    cite = pf.Cite(pf.Str('[@abc,'), pf.Space, pf.Str('p.23]'),
                   citations=[pf.Citation('abc', suffix=[pf.Str('IGNORED')])])
    assert pf.stringify(pf.Para(cite)) == '[@abc, p.23]\n\n'


def test_stringify_definition_list():
    dl = pf.DefinitionList(
        pf.DefinitionItem([pf.Str('Term'), pf.Space, pf.Emph(pf.Str('1'))],
                          [pf.Definition(pf.Plain(pf.Str('Definition'), pf.Space, pf.Str('1')))]),
        pf.DefinitionItem([pf.Str('Term 2')],
                          [pf.Definition(pf.Plain(pf.Str('2a'))), pf.Definition(pf.Plain(pf.Str('2b')))]))
    assert pf.stringify(dl) == '- Term 1: Definition 1\n- Term 2: 2a; 2b'


def test_stringify_note_is_inlined():
    # Current behaviour (see issue #225): note text is inlined without separation
    para = pf.Para(pf.Str('this'), pf.Note(pf.Para(pf.Str('note'))), pf.Space, pf.Str('is'))
    assert pf.stringify(para) == 'thisnote\n\n is\n\n'


def test_stringify_doc_includes_metadata_first():
    doc = pf.Doc(pf.Para(pf.Str('Hello'), pf.Space, pf.Str('world!')),
                 metadata={'a': True, 'b': 123.4, 'c': pf.MetaBlocks(pf.Para(pf.Str('!')))})
    assert pf.stringify(doc) == '123.4!\n\nHello world!\n\n'
    doc.content.append(pf.Para(pf.Str('More')))
    assert pf.stringify(doc).endswith('Hello world!\n\nMore\n\n')


def test_stringify_does_not_modify_the_tree():
    doc = load_path(JSON_FIXTURES / 'inlines.json')
    before = doc.to_json()
    pf.stringify(doc)
    assert doc.to_json() == before


# ---------------------------------------------------------------------------
# yaml_filter
# ---------------------------------------------------------------------------

def collect_yaml_calls(doc, **kwargs):
    calls = []

    def fenced_action(options, data, element, doc):
        assert isinstance(element, pf.CodeBlock)
        calls.append((dict(options), data))

    pf.run_filter(pf.yaml_filter, function=fenced_action, doc=doc, **kwargs)
    return calls


def test_yaml_filter_on_fenced_sample():
    doc = load_path(JSON_FIXTURES / 'sample-fenced.json')
    opts = {'foo': 'bar', 'bacon': True}
    assert collect_yaml_calls(doc, tag='spam') == [
        ({}, 'raw text'), ({}, 'raw text'), (opts, ''),
        (opts, 'raw text'), (opts, 'raw text'), (opts, 'raw text')]


def test_yaml_filter_strict_on_fenced_sample():
    doc = load_path(JSON_FIXTURES / 'sample-fenced.json')
    opts = {'foo': 'bar', 'bacon': True}
    assert collect_yaml_calls(doc, tag='eggs', strict_yaml=True) == [
        ({}, 'raw text'), ({}, 'raw text'), ({}, 'raw text'), ({}, 'raw text'),
        (opts, ''), (opts, ''), (opts, 'raw text'), (opts, 'raw text'), (opts, 'raw text'),
        ({'foo': 'bar', 'spam': 'eggs'}, 'raw1\nraw2\nthis\n...\nis\n...\nall raw')]


def test_yaml_filter_noop_leaves_document_unchanged():
    doc = load_path(JSON_FIXTURES / 'sample-fenced.json')
    before = doc.to_json()
    collect_yaml_calls(doc, tag='spam')
    collect_yaml_calls(doc, tag='eggs', strict_yaml=True)
    assert doc.to_json() == before


def test_yaml_filter_replaces_element_and_ignores_other_classes():
    def fenced_action(options, data, element, doc):
        return pf.Div(*[pf.HorizontalRule()] * options.get('count', 1), attributes={'data': data})

    doc = pf.Doc(pf.CodeBlock('count: 2\n---\nhello', classes=['foo']),
                 pf.CodeBlock('count: 3', classes=['bar']),
                 pf.Para(pf.Code('x', classes=['foo'])))
    pf.run_filter(pf.yaml_filter, tag='foo', function=fenced_action, doc=doc)
    div = doc.content[0]
    assert isinstance(div, pf.Div) and len(div.content) == 2
    assert div.attributes == {'data': 'hello'}
    assert isinstance(doc.content[1], pf.CodeBlock)
    assert isinstance(doc.content[2].content[0], pf.Code)


def test_yaml_filter_tags_dict():
    seen = []
    doc = pf.Doc(pf.CodeBlock('a: 1', classes=['one']), pf.CodeBlock('b: 2', classes=['two']))
    pf.run_filter(pf.yaml_filter, doc=doc, tags={
        'one': lambda options, data, element, doc: seen.append(('one', dict(options))),
        'two': lambda options, data, element, doc: seen.append(('two', dict(options))),
    })
    assert seen == [('one', {'a': 1}), ('two', {'b': 2})]


def test_yaml_filter_requires_exactly_one_of_tag_and_tags():
    block = pf.CodeBlock('x', classes=['a'])
    with pytest.raises(AssertionError):
        pf.yaml_filter(block, None)
    with pytest.raises(AssertionError):
        pf.yaml_filter(block, None, tag='a', tags={'a': print})


def test_yaml_filter_malformed_yaml(capsys):
    calls = []
    block = pf.CodeBlock('key: [unclosed\n---\ndata', classes=['t'])
    assert pf.yaml_filter(block, None, tag='t', function=lambda **kw: calls.append(kw)) is None
    assert calls == []
    assert 'malformed YAML block' in capsys.readouterr().err
    strict_block = pf.CodeBlock('---\nkey: "unclosed\n---\ndata', classes=['t'])
    assert pf.yaml_filter(strict_block, None, tag='t', function=lambda **kw: calls.append(kw),
                          strict_yaml=True) is None
    assert calls == []
    assert 'malformed YAML block' in capsys.readouterr().err


def test_yaml_filter_uses_safe_loader():
    calls = []
    block = pf.CodeBlock('x: !!python/object/apply:os.getcwd []', classes=['t'])
    with pytest.raises(yaml.constructor.ConstructorError):
        pf.yaml_filter(block, None, tag='t', function=lambda **kw: calls.append(kw))
    assert calls == []


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

def test_get_metadata_heavy_sample():
    doc = load_path(JSON_FIXTURES / 'sample-heavy_metadata.json')
    assert doc.get_metadata('title') == 'Lorem Ipsum: Title'
    assert type(doc.get_metadata('title', builtin=False)) is pf.MetaInlines
    assert doc.get_metadata('foobar', True) is True
    assert doc.get_metadata('foobar', 123) == 123
    assert doc.get_metadata('foobar') is None
    assert doc.get_metadata('abstract').startswith('Bring to the table win-win')
    assert doc.get_metadata('key1.key1-1') == ['value1-1-1', 'value1-1-2']
    assert doc.get_metadata('key1.missing', 'd') == 'd'
    assert doc.get_metadata('title.sub', 'd') == 'd'  # title is not a map
    meta = doc.get_metadata('amsthm.plain')
    assert type(meta) is list and meta[0]['Theorem'] == 'Lemma'
    assert doc.get_metadata('format.show-frame') is False
    assert len(doc.get_metadata('')) > 10
    assert isinstance(doc.get_metadata(builtin=False), pf.MetaMap)
    with pytest.raises(AssertionError):
        doc.get_metadata(1)


def test_get_metadata_from_python_values():
    doc = pf.Doc(pf.Para(pf.Str('x')), metadata={'a': True, 'b': 123.4})
    doc.metadata['d'] = False
    doc.metadata['e'] = pf.MetaBool(True)
    doc.metadata['f'] = {'A': 1233435353, 'B': 456}
    doc.metadata['f']['g'] = [1, 2, 3]
    assert doc.get_metadata('d') is False
    assert doc.get_metadata('e') is True
    assert doc.get_metadata('b') == '123.4'
    assert doc.get_metadata('f.A') == '1233435353'
    assert doc.get_metadata('f.e') is None
    assert doc.get_metadata('f.g') == ['1', '2', '3']


def test_meta2builtin():
    assert meta2builtin(pf.MetaBool(False)) is False
    assert meta2builtin(pf.MetaString('s')) == 's'
    assert meta2builtin(pf.MetaInlines(pf.Str('a'), pf.Space, pf.Emph(pf.Str('b')))) == 'a b'
    assert meta2builtin(pf.MetaBlocks(pf.Para(pf.Str('p')))) == 'p\n\n'
    assert meta2builtin(pf.MetaList('a', pf.MetaList('b'))) == ['a', ['b']]
    assert meta2builtin(pf.MetaMap(k=pf.MetaMap(j=True))) == {'k': {'j': True}}


def test_meta2builtin_unknown_value(capsys):
    assert meta2builtin('raw') == 'raw'
    assert 'MISSING' in capsys.readouterr().err


def test_get_option():
    doc = pf.Doc(metadata={'a': pf.MetaString('x'), 'b': pf.MetaMap(c=pf.MetaString('y'))})
    assert pf.get_option(default='a') == 'a'
    assert pf.get_option({'a': 1}, 'a') == 1
    assert pf.get_option({'a': None}, 'a', default=2) == 2
    assert pf.get_option({'a': None}, 'a', doc, 'a') == 'x'
    assert pf.get_option({}, 'missing', doc, 'a') == 'x'
    assert pf.get_option({'a': 0}, 'a', doc, 'a') == 0
    assert pf.get_option(doc=doc, doc_tag='b.c') == 'y'
    assert pf.get_option(doc=doc, doc_tag='b.missing', default='d') == 'd'
    assert pf.get_option(error_on_none=False) is None
    with pytest.raises(ValueError, match='could not retrieve a value'):
        pf.get_option({'a': None}, 'a', doc, 'missing')


# ---------------------------------------------------------------------------
# PandocVersion (with a fake `pandoc --version`)
# ---------------------------------------------------------------------------

FAKE_VERSION = """pandoc 3.1.13
Features: +server +lua
Scripting engine: Lua 5.4
User data directory: /home/user/.local/share/pandoc or /home/user/.pandoc
Copyright (C) 2006-2023 John MacFarlane. Web: https://pandoc.org
"""


@pytest.fixture
def fake_pandoc_version(monkeypatch):
    calls = []

    def fake_run_pandoc(text='', args=None, pandoc_path=None):
        calls.append(args)
        return FAKE_VERSION
    monkeypatch.setattr(tools, 'run_pandoc', fake_run_pandoc)
    return calls


def test_pandoc_version_parsing(fake_pandoc_version):
    v = tools.PandocVersion()
    assert str(v) == '3.1.13'
    assert v.version == (3, 1, 13)
    assert repr(v) == FAKE_VERSION
    assert v.data_dir == ['/home/user/.local/share/pandoc/filters', '/home/user/.pandoc/filters']
    assert fake_pandoc_version[0] == ['--version']


def test_get_filter_dirs_with_fake_pandoc(fake_pandoc_version, monkeypatch):
    import panflute.autofilter as autofilter
    monkeypatch.setattr(tools, 'pandoc_version', tools.PandocVersion())
    monkeypatch.setenv('HOME', '/home/user')
    if sys.platform != 'win32':
        assert autofilter.get_filter_dirs() == ['/home/user/.local/share/pandoc/filters']
    assert autofilter.get_filter_dirs(hardcoded=False) == [
        '/home/user/.local/share/pandoc/filters', '/home/user/.pandoc/filters']


@pytest.mark.skipif(sys.platform == 'win32', reason='POSIX filter dirs')
def test_get_filter_dirs_old_pandoc(monkeypatch):
    import panflute.autofilter as autofilter
    monkeypatch.setattr(tools, 'run_pandoc', lambda *a, **k: FAKE_VERSION.replace('3.1.13', '2.11.4'))
    monkeypatch.setattr(tools, 'pandoc_version', tools.PandocVersion())
    monkeypatch.setenv('HOME', '/home/user')
    assert autofilter.get_filter_dirs() == ['/home/user/.pandoc/filters',
                                            '/home/user/.local/share/pandoc/filters']


# ---------------------------------------------------------------------------
# debug and shell
# ---------------------------------------------------------------------------

def test_debug_prints_to_stderr(capsys):
    pf.debug('a', 1, sep='-', end='!')
    out, err = capsys.readouterr()
    assert out == '' and err == 'a-1!'


def test_shell_list_and_string():
    py = sys.executable
    assert pf.shell([py, '-c', 'print("hi")']).strip() == b'hi'
    assert pf.shell([py, '-c', 'import sys; sys.stdout.write(sys.stdin.read().upper())'],
                    msg=b'abc') == b'ABC'
    if sys.platform != 'win32':
        assert pf.shell(f'"{py}" -c "print(1)"').strip() == b'1'


def test_shell_failure_raises_ioerror(capsys):
    with pytest.raises(IOError):
        pf.shell([sys.executable, '-c', 'import sys; sys.stderr.write("boom"); sys.exit(3)'])
    assert 'boom' in capsys.readouterr().err


# ---------------------------------------------------------------------------
# run_pandoc / convert_text without pandoc
# ---------------------------------------------------------------------------

def test_run_pandoc_without_pandoc_on_path(monkeypatch):
    monkeypatch.setattr(tools, 'PANDOC_PATH', None)
    monkeypatch.setattr(tools, 'which', lambda name: None)
    with pytest.raises(OSError, match='does not exist'):
        pf.run_pandoc('x')


def test_run_pandoc_with_invalid_pandoc_path(tmp_path):
    with pytest.raises(OSError, match='is invalid'):
        pf.run_pandoc('x', pandoc_path=str(tmp_path / 'no-such-pandoc'))


def test_run_pandoc_with_custom_pandoc_path(tmp_path):
    if sys.platform == 'win32':
        pytest.skip('uses a shell script as fake pandoc')
    fake = tmp_path / 'fake-pandoc'
    # Only shell builtins: the test must also work with an empty PATH
    fake.write_text('#!/bin/sh\nprintf "args: %s\\n" "$*"\n'
                    'while IFS= read -r line || [ -n "$line" ]; do printf "%s\\n" "$line"; done\n')
    fake.chmod(0o755)
    assert pf.run_pandoc('input', args=['-a', 'b'], pandoc_path=str(fake)) == 'args: -a b\ninput\n'
    assert pf.convert_text('in', input_format='latex', output_format='html', pandoc_path=str(fake),
                           extra_args=['--x']) == 'args: --from=latex --to=html --x\nin'


# ---------------------------------------------------------------------------
# run_pandoc / convert_text with pandoc
# ---------------------------------------------------------------------------


@pytest.mark.requires_pandoc
def test_run_pandoc():
    assert pf.run_pandoc('*a*', ['--to=html']).strip() == '<p><em>a</em></p>'
    assert pf.run_pandoc(args=['--version']).startswith('pandoc')
    with pytest.raises(IOError):
        pf.run_pandoc('x', ['--from=not-a-format'])


@pytest.mark.requires_pandoc
def test_pandoc_version_with_pandoc():
    v = tools.pandoc_version
    assert len(v.version) >= 2 and v.version >= (2, 11)
    assert str(v) == '.'.join(map(str, v.version))
    assert all(d.endswith('filters') for d in v.data_dir)
    out = subprocess.run([PANDOC, '--version'], capture_output=True, text=True).stdout
    assert out.splitlines()[0].endswith(f' {v}')


@pytest.mark.requires_pandoc
def test_convert_text_markdown_to_panflute():
    md = 'Some *markdown* **text** ~xyz~'
    expected = [pf.Para(pf.Str('Some'), pf.Space, pf.Emph(pf.Str('markdown')), pf.Space,
                        pf.Strong(pf.Str('text')), pf.Space, pf.Subscript(pf.Str('xyz')))]
    result = pf.convert_text(md)
    assert isinstance(result, list)
    assert result == expected
    assert repr(result) == repr(expected)


@pytest.mark.requires_pandoc
def test_convert_text_latex():
    tex = r'Some $x^y$ or $x_n = \sqrt{a + b}$ \textit{a}'
    expected = [pf.Para(pf.Str('Some'), pf.Space, pf.Math('x^y', format='InlineMath'), pf.Space,
                        pf.Str('or'), pf.Space, pf.Math(r'x_n = \sqrt{a + b}', format='InlineMath'),
                        pf.Space, pf.RawInline(r'\textit{a}', format='tex'))]
    assert pf.convert_text(tex) == expected
    assert pf.convert_text(tex, input_format='latex') == [
        pf.Para(pf.Str('Some'), pf.Space, pf.Math('x^y', format='InlineMath'), pf.Space,
                pf.Str('or'), pf.Space, pf.Math(r'x_n = \sqrt{a + b}', format='InlineMath'),
                pf.Space, pf.Emph(pf.Str('a')))]


@pytest.mark.requires_pandoc
def test_convert_text_standalone_returns_doc():
    doc = pf.convert_text('---\ntitle: T\n---\n\ntext', standalone=True)
    assert isinstance(doc, pf.Doc)
    assert doc.get_metadata('title') == 'T'
    assert doc.content == pf.Doc(pf.Para(pf.Str('text'))).content
    assert doc.api_version[:2] >= (1, 22)


@pytest.mark.requires_pandoc
def test_convert_text_to_and_from_json_strings():
    md = 'Some *markdown* **text** ~xyz~'
    as_json = pf.convert_text(md, input_format='markdown', output_format='json')
    assert isinstance(as_json, str) and '"pandoc-api-version"' in as_json
    assert pf.convert_text(as_json, input_format='json', output_format='markdown') == md


@pytest.mark.requires_pandoc
@pytest.mark.parametrize('standalone', [False, True])
def test_convert_text_panflute_roundtrip(standalone):
    md = 'Some *markdown* **text** ~xyz~'
    tree = pf.convert_text(md, input_format='markdown', output_format='panflute', standalone=standalone)
    assert pf.convert_text(tree, input_format='panflute', output_format='markdown') == md


@pytest.mark.requires_pandoc
def test_convert_text_panflute_input_variants():
    para = pf.Para(pf.Emph(pf.Str('x')))
    assert pf.convert_text(para, input_format='panflute', output_format='markdown') == '*x*'
    assert pf.convert_text([para, para], input_format='panflute', output_format='markdown') == '*x*\n\n*x*'
    # A Doc is passed to pandoc as is, so its api_version must be the one of
    # the installed pandoc (lists and elements get it automatically)
    api_version = pf.convert_text('', standalone=True).api_version
    doc = pf.Doc(para, api_version=api_version)
    assert pf.convert_text(doc, input_format='panflute', output_format='html') == '<p><em>x</em></p>'
    elems = pf.convert_text(para, input_format='panflute', output_format='panflute')
    assert elems == [para]


@pytest.mark.requires_pandoc
def test_convert_text_normalises_newlines():
    out = pf.convert_text('a\n\nb', output_format='markdown')
    assert '\r' not in out
    assert out == 'a\n\nb'


@pytest.mark.requires_pandoc
@pytest.mark.parametrize('md,fmt', [
    ('lorem\n\n  --- ---\n  x   y\n  --- ---\n\nipsum', 'markdown'),
    ('lorem\n\n| x   | y   |\n|-----|-----|\n\nipsum', 'gfm'),
])
def test_convert_text_table_roundtrips(md, fmt):
    via_json = pf.convert_text(md, input_format=fmt, output_format='json', standalone=True)
    assert pf.convert_text(via_json, input_format='json', output_format=fmt) == md
    via_panflute = pf.convert_text(md, input_format=fmt, output_format='panflute', standalone=True)
    assert pf.convert_text(via_panflute, input_format='panflute', output_format=fmt) == md


@pytest.mark.requires_pandoc
def test_convert_text_extra_args():
    out = pf.convert_text('# A', output_format='html', extra_args=['--shift-heading-level-by=1'])
    assert out.startswith('<h2')
    out = pf.convert_text('x', output_format='html', standalone=True,
                          extra_args=['--metadata=title:T'])
    assert out.startswith('<!DOCTYPE html>')
