"""
Round trips through the pandoc installed on the machine (whatever its
version): pandoc output -> panflute -> pandoc must be lossless.

The stored-fixture equivalents of these tests (test_golden.py) do not need
pandoc but only exercise the pandoc version that generated the fixtures;
these ones check panflute against the pandoc version used in CI.
"""

import json
import subprocess

import pytest

import panflute as pf

from .helpers import CORPUS, PANDOC, SAMPLE_FILES, dump_text, load_text

pytestmark = pytest.mark.requires_pandoc

SOURCES = (
    [(p, 'markdown') for p in sorted(CORPUS.glob('*.md'))]
    + [(CORPUS / 'tables.html', 'html')]
    + [(p, 'markdown') for p in sorted(SAMPLE_FILES.glob('*/example.md'))]
    + [(p, 'native') for p in sorted((SAMPLE_FILES / 'native').glob('*.native'))]
)
IDS = [f'{p.parent.name}/{p.name}' for p, _ in SOURCES]


def pandoc(*args, text=None):
    proc = subprocess.run([PANDOC, *map(str, args)], input=text, capture_output=True,
                          text=True, encoding='utf-8')
    assert proc.returncode == 0, proc.stderr
    return proc.stdout


@pytest.mark.parametrize('source,fmt', SOURCES, ids=IDS)
def test_panflute_output_is_lossless_for_pandoc(source, fmt):
    json_pandoc = pandoc(f'--from={fmt}', '--to=json', source)
    doc = load_text(json_pandoc)
    json_panflute = dump_text(doc)

    # Same JSON value as pandoc's own output
    assert json.loads(json_panflute) == json.loads(json_pandoc)

    # And pandoc reads it back to the same document
    native_pandoc = pandoc('--from=json', '--to=native', '--standalone', text=json_pandoc)
    native_panflute = pandoc('--from=json', '--to=native', '--standalone', text=json_panflute)
    assert native_panflute == native_pandoc

    # Also after a walk that changes nothing
    doc.walk(lambda elem, doc: None)
    assert dump_text(doc) == json_panflute


@pytest.mark.parametrize('source,fmt', SOURCES[:3], ids=IDS[:3])
def test_convert_text_roundtrip(source, fmt):
    text = source.read_text(encoding='utf-8')
    json_pandoc = pf.convert_text(text, input_format=fmt, output_format='json', standalone=True)
    doc = pf.convert_text(json_pandoc, input_format='json', output_format='panflute', standalone=True)
    json_panflute = pf.convert_text(doc, input_format='panflute', output_format='json', standalone=True)
    assert json_pandoc == json_panflute


@pytest.mark.parametrize('markdown_text,expected_text', [
    ('Hello **world**! *How* are ~you~ doing?', 'Hello world! How are you doing?\n\n'),
    ('[@abc, p.23]', '[@abc, p.23]\n\n'),
    ('Term 1\n:   Definition 1\n\nTerm 2 with *inline markup*\n\n:   Definition 2',
     '- Term 1: Definition 1\n- Term 2 with inline markup: Definition 2\n\n'),
    ('Term 1\n~ Definition 1\n\nTerm 2\n~ Definition 2a\n~ Definition 2b',
     '- Term 1: Definition 1\n- Term 2: Definition 2a; Definition 2b'),
])
def test_stringify_markdown(markdown_text, expected_text):
    doc = pf.convert_text(markdown_text, input_format='markdown', output_format='panflute', standalone=True)
    assert pf.stringify(doc) == expected_text


def test_doc_from_convert_text_has_no_pandoc_environment(monkeypatch):
    monkeypatch.delenv('PANDOC_VERSION', raising=False)
    monkeypatch.delenv('PANDOC_READER_OPTIONS', raising=False)
    doc = pf.convert_text('*x*', standalone=True)
    assert doc.pandoc_version is None
    assert doc.pandoc_reader_options == {}
