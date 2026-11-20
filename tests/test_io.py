"""
Tests for panflute.io (load, dump, run_filter(s), toJSONFilter(s)) and the
pandoc environment variables exposed on Doc.
"""

import io
import json
import subprocess
import sys

import pytest

import panflute as pf

from .helpers import FILTERS, PANDOC, dump_text, load_text


SIMPLE = '{"pandoc-api-version":[1,23,1],"meta":{},"blocks":[{"t":"Para","c":[{"t":"Str","c":"héllo"}]}]}'


def test_load_from_stream():
    doc = pf.load(io.StringIO(SIMPLE))
    assert isinstance(doc, pf.Doc)
    assert doc.api_version == (1, 23, 1)
    assert doc.content[0].content[0].text == 'héllo'


def test_load_sets_format_from_argv(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['filter.py', 'latex'])
    assert pf.load(io.StringIO(SIMPLE)).format == 'latex'
    monkeypatch.setattr(sys, 'argv', ['filter.py'])
    assert pf.load(io.StringIO(SIMPLE)).format == 'html'


def test_load_from_stdin_reads_utf8_bytes(monkeypatch):
    monkeypatch.setattr(sys, 'stdin', io.TextIOWrapper(io.BytesIO(SIMPLE.encode('utf-8')), encoding='latin-1'))
    doc = pf.load()
    assert doc.content[0].content[0].text == 'héllo'


def test_load_rejects_non_documents():
    with pytest.raises(AssertionError):
        pf.load(io.StringIO('[]'))
    with pytest.raises(json.JSONDecodeError):
        pf.load(io.StringIO('not json'))
    with pytest.raises(TypeError, match='invalid api version'):
        pf.load(io.StringIO('{"pandoc-api-version":[1,20],"meta":{},"blocks":[]}'))


def test_dump_to_stream_is_compact_and_unescaped():
    doc = pf.Doc(pf.Para(pf.Str('héllo'), pf.Space, pf.Str('"q"')), api_version=(1, 23, 1))
    out = dump_text(doc)
    assert out == ('{"pandoc-api-version":[1,23,1],"meta":{},"blocks":[{"t":"Para","c":'
                   '[{"t":"Str","c":"héllo"},{"t":"Space"},{"t":"Str","c":"\\"q\\""}]}]}')


def test_dump_to_stdout_writes_utf8(monkeypatch):
    buffer = io.BytesIO()
    monkeypatch.setattr(sys, 'stdout', io.TextIOWrapper(buffer, encoding='ascii'))
    pf.dump(pf.Doc(pf.Para(pf.Str('héllo')), api_version=(1, 23, 1)))
    sys.stdout.flush()
    assert buffer.getvalue().decode('utf-8') == SIMPLE


def test_dump_requires_doc():
    with pytest.raises(TypeError, match='panflute.Doc'):
        pf.dump(pf.Para(), io.StringIO())
    with pytest.raises(TypeError):
        pf.dump([pf.Para()], io.StringIO())


def test_load_dump_roundtrip():
    assert dump_text(load_text(SIMPLE)) == SIMPLE


# ---------------------------------------------------------------------------
# run_filter(s) and wrappers
# ---------------------------------------------------------------------------

def upper(elem, doc):
    if isinstance(elem, pf.Str):
        return pf.Str(elem.text.upper())


def test_run_filter_streams():
    out = io.StringIO()
    result = pf.run_filter(upper, input_stream=io.StringIO(SIMPLE), output_stream=out)
    assert result is None
    assert out.getvalue() == SIMPLE.replace('héllo', 'HÉLLO')


def test_run_filters_streams_with_prepare_finalize_kwargs(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['f', 'markdown'])
    events = []

    def prepare(doc):
        events.append(('prepare', doc.format))

    def suffix(elem, doc, text):
        if isinstance(elem, pf.Str):
            elem.text += text

    def upper_kw(elem, doc, text):
        # keyword arguments are passed to every action
        assert text == '!'
        return upper(elem, doc)

    def finalize(doc):
        events.append(('finalize', doc.content[0].content[0].text))
        doc.content.append(pf.HorizontalRule())

    out = io.StringIO()
    pf.run_filters([suffix, upper_kw], prepare=prepare, finalize=finalize,
                   input_stream=io.StringIO(SIMPLE), output_stream=out, text='!')
    assert events == [('prepare', 'markdown'), ('finalize', 'HÉLLO!')]
    assert json.loads(out.getvalue())['blocks'][-1] == {'t': 'HorizontalRule'}


def test_run_filter_from_stdin_to_stdout(monkeypatch):
    monkeypatch.setattr(sys, 'stdin', io.TextIOWrapper(io.BytesIO(SIMPLE.encode('utf-8'))))
    buffer = io.BytesIO()
    monkeypatch.setattr(sys, 'stdout', io.TextIOWrapper(buffer))
    pf.run_filter(upper)
    sys.stdout.flush()
    assert buffer.getvalue().decode('utf-8') == SIMPLE.replace('héllo', 'HÉLLO')


def test_tojsonfilter_wrappers():
    out = io.StringIO()
    pf.toJSONFilter(upper, input_stream=io.StringIO(SIMPLE), output_stream=out)
    assert 'HÉLLO' in out.getvalue()
    out = io.StringIO()
    pf.toJSONFilters([upper], input_stream=io.StringIO(SIMPLE), output_stream=out)
    assert 'HÉLLO' in out.getvalue()
    doc = load_text(SIMPLE)
    assert pf.toJSONFilter(upper, doc=doc) is doc
    assert pf.toJSONFilters([upper], doc=doc) is doc


def test_run_filters_with_no_actions():
    out = io.StringIO()
    pf.run_filters([], input_stream=io.StringIO(SIMPLE), output_stream=out)
    assert out.getvalue() == SIMPLE


# ---------------------------------------------------------------------------
# Environment variables set by pandoc
# ---------------------------------------------------------------------------

def test_doc_without_pandoc_environment(monkeypatch):
    monkeypatch.delenv('PANDOC_VERSION', raising=False)
    monkeypatch.delenv('PANDOC_READER_OPTIONS', raising=False)
    doc = load_text(SIMPLE)
    assert doc.pandoc_version is None
    assert doc.pandoc_reader_options == {}


def test_doc_reads_pandoc_environment(monkeypatch):
    monkeypatch.setenv('PANDOC_VERSION', '3.1.13')
    monkeypatch.setenv('PANDOC_READER_OPTIONS', '{"standalone": false, "columns": 80}')
    doc = pf.Doc()
    assert doc.pandoc_version == (3, 1, 13)
    assert doc.pandoc_reader_options == {'standalone': False, 'columns': 80}


def test_doc_malformed_pandoc_environment(monkeypatch, capsys):
    monkeypatch.setenv('PANDOC_VERSION', '3.x')
    monkeypatch.setenv('PANDOC_READER_OPTIONS', '{not json')
    doc = pf.Doc()
    assert doc.pandoc_version is None
    assert doc.pandoc_reader_options == {}
    err = capsys.readouterr().err
    assert 'PANDOC_VERSION is malformed' in err
    assert 'PANDOC_READER_OPTIONS is malformed' in err


@pytest.mark.requires_pandoc
def test_filter_run_by_pandoc_sees_environment(filter_env):
    # assert_env.py asserts that PANDOC_VERSION and PANDOC_READER_OPTIONS are set
    proc = subprocess.run([PANDOC, f'--filter={FILTERS / "assert_env.py"}', '--to=plain'],
                          input='Hello!', capture_output=True, text=True, env=filter_env)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == 'Hello!'
    assert 'Pandoc version:' in proc.stderr


@pytest.mark.requires_pandoc
@pytest.mark.parametrize('filter_name,last_inline', [
    ('do_nothing.py', pf.Strong),
    ('underline.py', pf.Underline),
])
def test_python_filters_run_by_pandoc(filter_env, filter_name, last_inline):
    # Compare the resulting document rather than pandoc's Markdown, whose
    # spelling varies across versions (e.g. pandoc 2.11 writes underlined text
    # as [b]{.ul}, later versions as [b]{.underline})
    proc = subprocess.run([PANDOC, f'--filter={FILTERS / filter_name}', '--to=json'],
                          input='Some *a* **b**', capture_output=True, text=True, env=filter_env)
    assert proc.returncode == 0, proc.stderr
    doc = load_text(proc.stdout)
    expected = pf.Para(pf.Str('Some'), pf.Space(), pf.Emph(pf.Str('a')), pf.Space(), last_inline(pf.Str('b')))
    assert list(doc.content) == [expected]
