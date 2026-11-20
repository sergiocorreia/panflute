"""
Tests for panflute.autofilter: the ``panflute``/``panfl`` command line
interfaces, ``stdio()`` and the search for filters.

Filters are listed either as arguments or in the document metadata:
  panflute-filters  : a string or list
  panflute-path     : optional folder(s) that contain filters
  panflute-verbose  : True to display debugging info
  panflute-echo     : message to display on success

The test filter (fixtures/panfl/*/test_filter.py) replaces "-" with "+" in
math, and appends the output format.
"""

import io
import json
import subprocess
import sys

import pytest
from click.testing import CliRunner

import panflute as pf
from panflute.autofilter import autorun_filters

from .helpers import EXAMPLES, FIXTURES, PANDOC, dump_text, load_text

PANFL = FIXTURES / 'panfl'

pytestmark = pytest.mark.usefixtures('clean_import_state', 'fake_stdout')


@pytest.fixture
def fake_stdout(monkeypatch):
    """
    Point sys.__stdout__ to an in-memory UTF-8 stream, so that no test can
    write to the real stdout of the pytest process. Returns the underlying
    bytes buffer; tests that read what was written to sys.stdout must call
    redirect_stdout() in the test body (pytest's own output capturing sets
    sys.stdout again after the fixtures are set up).
    """
    buffer = io.BytesIO()
    stream = io.TextIOWrapper(buffer, encoding='utf-8')
    monkeypatch.setattr(sys, '__stdout__', stream)
    return buffer


def redirect_stdout(monkeypatch, buffer):
    monkeypatch.setattr(sys, 'stdout', io.TextIOWrapper(buffer, encoding='utf-8'))


def stdout_text(buffer):
    sys.stdout.flush()
    return buffer.getvalue().decode('utf-8')


def doc_json(blocks=None, meta=None):
    """A pandoc JSON document whose content is the math expression $1-1$."""
    if blocks is None:
        blocks = [{'t': 'Para', 'c': [{'t': 'Math', 'c': [{'t': 'InlineMath'}, '1-1']}]}]
    meta = {k: {'t': 'MetaString', 'c': v} if isinstance(v, str) else v
            for k, v in (meta or {}).items()}
    return json.dumps({'pandoc-api-version': [1, 23, 1], 'meta': meta, 'blocks': blocks})


def math_text(output):
    blocks = json.loads(output)['blocks']
    return blocks[0]['c'][0]['c'][1]


def run_stdio(*args, input_text, fmt='markdown', **kwargs):
    sys.argv[1:] = [fmt]
    out = io.StringIO()
    pf.stdio(*args, input_stream=io.StringIO(input_text), output_stream=out, **kwargs)
    return out.getvalue()


# ---------------------------------------------------------------------------
# stdio
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('panfl_', [True, False])
def test_stdio_filters_from_metadata(panfl_):
    text = doc_json(meta={'panflute-filters': 'test_filter', 'panflute-path': str(PANFL / 'bar')})
    out = run_stdio(None, None, False, True, panfl_, input_text=text)
    assert math_text(out) == '1+1markdown'


def test_stdio_filter_list_and_relative_path_in_metadata(monkeypatch):
    monkeypatch.chdir(FIXTURES)
    text = doc_json(meta={
        'panflute-filters': {'t': 'MetaList', 'c': [{'t': 'MetaString', 'c': 'test_filter'},
                                                    {'t': 'MetaString', 'c': 'test_filter.py'}]},
        'panflute-path': {'t': 'MetaList', 'c': [{'t': 'MetaString', 'c': './panfl/bar'},
                                                 {'t': 'MetaString', 'c': '--no-sys-path'}]},
    })
    out = run_stdio(input_text=text, fmt='latex', data_dir=False)
    # The same module runs twice
    assert math_text(out) == '1+1latexlatex'


def test_stdio_filter_file_in_search_dir():
    out = run_stdio(['test_filter.py'], [str(PANFL / 'bar')], False, True, False, input_text=doc_json())
    assert math_text(out) == '1+1markdown'


def test_stdio_filter_absolute_path():
    out = run_stdio([str(PANFL / 'bar' / 'test_filter.py')], [], False, True, True, input_text=doc_json())
    assert math_text(out) == '1+1markdown'


def test_stdio_filter_as_package_module():
    out = run_stdio(['foo.test_filter'], [str(PANFL)], False, True, True, input_text=doc_json())
    assert math_text(out) == '1+1markdown'


def test_stdio_filter_as_module_in_package_dir():
    out = run_stdio(['test_filter'], [str(PANFL / 'foo')], False, True, True, input_text=doc_json())
    assert math_text(out) == '1+1markdown'


def test_stdio_search_dirs_options_in_metadata(monkeypatch, capsys):
    import panflute.autofilter as autofilter
    monkeypatch.setattr(autofilter, 'get_filter_dirs', lambda: ['/data/dir/filters'])
    text = doc_json(meta={
        'panflute-filters': 'test_filter',
        'panflute-verbose': {'t': 'MetaBool', 'c': True},
        'panflute-path': {'t': 'MetaList', 'c': [{'t': 'MetaString', 'c': str(PANFL / 'bar')},
                                                 {'t': 'MetaString', 'c': '--data-dir'},
                                                 {'t': 'MetaString', 'c': '--no-sys-path'}]},
    })
    out = run_stdio(None, None, False, True, True, input_text=text)
    assert math_text(out) == '1+1markdown'
    err = capsys.readouterr().err
    assert 'data_dir=True sys_path=False' in err
    assert '/data/dir/filters' in err


@pytest.mark.parametrize('panfl_', [True, False])
def test_stdio_search_order(monkeypatch, capsys, panfl_):
    import panflute.autofilter as autofilter
    monkeypatch.setattr(autofilter, 'get_filter_dirs', lambda: ['DATADIR'])
    text = doc_json(meta={'panflute-verbose': {'t': 'MetaBool', 'c': True}})
    run_stdio(None, ['first'], True, True, panfl_, input_text=text)
    err = capsys.readouterr().err
    folders = err.split('search for filters in the following folders:\n', 1)[1].splitlines()[0]
    folders = [f.strip('"') for f in folders.split('" "')]
    if panfl_:
        assert folders[:2] == ['first', 'DATADIR']
        assert '.' not in folders and '' not in folders
    else:
        assert folders[:3] == ['first', '.', 'DATADIR']
    assert set(autofilter.reduced_sys_path) <= set(folders)


def test_stdio_verbose_reports_missing_absolute_filter(capsys):
    missing = str(PANFL / 'missing.py')
    with pytest.raises(Exception, match='filter not found'):
        autorun_filters([missing], load_text(doc_json()), ['.'], True)
    assert f'NOT found in {missing}' in capsys.readouterr().err


def test_stdio_without_filters_is_noop(capsys):
    text = doc_json(meta={'panflute-verbose': {'t': 'MetaBool', 'c': True}})
    out = run_stdio(None, [], False, False, input_text=text)
    assert json.loads(out) == json.loads(text)
    assert 'no filters were provided' in capsys.readouterr().err


def test_stdio_echo_and_verbose(capsys):
    text = doc_json(meta={'panflute-echo': 'Hello world!',
                          'panflute-verbose': {'t': 'MetaBool', 'c': True}})
    run_stdio(['test_filter'], [str(PANFL / 'bar')], False, False, input_text=text)
    err = capsys.readouterr().err
    assert 'Hello world!' in err
    assert 'panflute: will run the following filters: test_filter' in err
    assert 'found in' in err and 'completed' in err


def test_stdio_filter_not_found():
    with pytest.raises(Exception, match='filter not found: does_not_exist'):
        run_stdio(['does_not_exist'], [str(PANFL)], False, False, input_text=doc_json())
    with pytest.raises(Exception, match='filter not found'):
        run_stdio([str(PANFL / 'missing.py')], [], False, False, input_text=doc_json())


def test_main_reads_stdin_and_writes_stdout(monkeypatch, fake_stdout):
    import panflute.autofilter as autofilter
    monkeypatch.setattr(autofilter, 'get_filter_dirs', lambda: [])  # would run pandoc
    monkeypatch.setattr(sys, 'argv', ['panflute', 'html'])
    text = doc_json(meta={'panflute-filters': 'test_filter', 'panflute-path': str(PANFL / 'bar')})
    monkeypatch.setattr(sys, 'stdin', io.TextIOWrapper(io.BytesIO(text.encode('utf-8'))))
    redirect_stdout(monkeypatch, fake_stdout)
    pf.main()
    assert math_text(stdout_text(fake_stdout)) == '1+1html'


# ---------------------------------------------------------------------------
# autorun_filters
# ---------------------------------------------------------------------------

def write_filter(path, body):
    path.write_text('import panflute as pf\n\n' + body, encoding='utf-8')
    return path


def test_autorun_filters_order_and_stdout_interception(tmp_path, capsys, monkeypatch):
    write_filter(tmp_path / 'first.py',
                 'def main(doc):\n    print("noise")\n    doc.content.append(pf.Para(pf.Str("1")))\n')
    write_filter(tmp_path / 'second.py',
                 'def main(doc):\n    doc.content.append(pf.Para(pf.Str("2")))\n')
    doc = load_text(doc_json(blocks=[]))
    result = autorun_filters(['first', 'second.py'], doc, [str(tmp_path)], False)
    assert result is doc
    assert [b.content[0].text for b in doc.content] == ['1', '2']
    err = capsys.readouterr().err
    assert 'wrote to stdout' in err and 'noise' in err


def test_autorun_filters_failure_reports_filter(tmp_path, capsys, monkeypatch):
    write_filter(tmp_path / 'broken.py', 'def main(doc):\n    raise ValueError("boom")\n')
    write_filter(tmp_path / 'nomain.py', 'x = 1\n')
    with pytest.raises(Exception, match='boom'):
        autorun_filters(['broken'], load_text(doc_json()), [str(tmp_path)], False)
    assert 'Failed to run filter: broken' in capsys.readouterr().err
    with pytest.raises(Exception):
        autorun_filters(['nomain'], load_text(doc_json()), [str(tmp_path)], False)
    assert 'filter lacks a main() function' in capsys.readouterr().err


# ---------------------------------------------------------------------------
# panfl CLI (through click's CliRunner)
# ---------------------------------------------------------------------------

def test_panfl_help():
    result = CliRunner().invoke(pf.panfl, ['--help'])
    assert result.exit_code == 0
    assert 'Allows Panflute to be run as a command line executable' in result.output
    for option in ('--to', '--dir', '--data-dir', '--no-sys-path'):
        assert option in result.output


def run_panfl(args, input_text, monkeypatch, fake_stdout):
    # Not through CliRunner: its output capture did not survive autorun_filters()
    # resetting sys.stdout to sys.__stdout__ (fixed in 3.0).
    monkeypatch.setattr(sys, 'stdin', io.TextIOWrapper(io.BytesIO(input_text.encode('utf-8'))))
    redirect_stdout(monkeypatch, fake_stdout)
    pf.panfl.main(args, standalone_mode=False)
    return stdout_text(fake_stdout)


def test_panfl_with_to_option(monkeypatch, fake_stdout):
    out = run_panfl(['test_filter', '-t', 'latex', '-d', str(PANFL / 'bar')], doc_json(),
                    monkeypatch, fake_stdout)
    assert math_text(out) == '1+1latex'
    assert sys.argv[1:] == ['latex']


def test_panfl_with_to_option_several_filters_and_dirs(monkeypatch, fake_stdout):
    out = run_panfl(['test_filter', 'foo.test_filter', '--to', 'html', '--dir', str(PANFL / 'bar'),
                     '-d', str(PANFL), '--no-sys-path'], doc_json(), monkeypatch, fake_stdout)
    assert math_text(out) == '1+1htmlhtml'


def test_panfl_filter_mode_reads_metadata(monkeypatch, fake_stdout):
    text = doc_json(meta={'panflute-filters': 'test_filter', 'panflute-path': str(PANFL / 'bar')})
    sys.argv[1:] = ['html']
    out = run_panfl(['html'], text, monkeypatch, fake_stdout)
    assert math_text(out) == '1+1html'


@pytest.mark.parametrize('args', [
    ['a', 'b'],
    ['a', '-d', 'dir'],
    ['a', '--data-dir'],
])
def test_panfl_filter_mode_rejects_options(args):
    result = CliRunner().invoke(pf.panfl, args, input=doc_json())
    assert result.exit_code != 0
    assert isinstance(result.exception, ValueError)
    assert 'only one positional argument' in str(result.exception)


def test_panfl_passes_options_to_stdio(monkeypatch):
    import panflute.autofilter as autofilter
    calls = []
    monkeypatch.setattr(autofilter, 'stdio', lambda *args, **kwargs: calls.append((args, kwargs)))
    pf.panfl.main(['f1', 'f2', '-t', 'latex', '-d', 'd1', '--dir', 'd2', '--data-dir'],
                  standalone_mode=False)
    pf.panfl.main(['latex'], standalone_mode=False)
    assert calls == [
        ((['f1', 'f2'], ['d1', 'd2'], True, True), {'panfl_': True}),
        ((None, None, False, True), {'panfl_': True}),
    ]


# ---------------------------------------------------------------------------
# Through pandoc
# ---------------------------------------------------------------------------

@pytest.mark.requires_pandoc
def test_get_filter_dirs_types():
    dirs = pf.get_filter_dirs()
    assert isinstance(dirs, list) and all(isinstance(d, str) for d in dirs)


@pytest.mark.requires_pandoc
def test_get_filter_dirs_matches_pandoc():
    assert sorted(pf.get_filter_dirs()) == sorted(pf.get_filter_dirs(hardcoded=False))


def run_pandoc_process(args, stdin, env, cwd=None):
    proc = subprocess.run([PANDOC, *args], input=stdin, capture_output=True, text=True,
                          env=env, cwd=cwd)
    assert proc.returncode == 0, proc.stderr
    return proc.stdout.strip(), proc.stderr


@pytest.mark.requires_pandoc
@pytest.mark.parametrize('executable', ['panfl', 'panflute'])
def test_pandoc_filter_absolute_path(filter_env, executable):
    out, _ = run_pandoc_process(
        [f'--filter={executable}', '--to=markdown', '--metadata=panflute-verbose:True',
         f'--metadata=panflute-filters:{PANFL / "bar" / "test_filter.py"}'],
        '$1-1$', filter_env)
    assert out == '$1+1markdown$'


@pytest.mark.requires_pandoc
def test_pandoc_filter_relative_path(filter_env):
    out, _ = run_pandoc_process(
        ['--filter=panfl', '--to=markdown', '--metadata=panflute-filters:test_filter',
         '--metadata=panflute-path:./panfl/bar'],
        '$1-1$', filter_env, cwd=FIXTURES)
    assert out == '$1+1markdown$'


@pytest.mark.requires_pandoc
def test_pandoc_filter_example_filters_from_yaml(filter_env):
    """The caps and headers example filters, listed in the YAML block."""
    # (panflute-path is passed on the command line: in the YAML block it would
    # be parsed as markdown, and e.g. "--" in the path would become a dash)
    md = """---
title: Some Title
panflute-echo: "Hello world!"
panflute-verbose: False
panflute-filters: [caps, headers]
...

# Level 1

## Level 2

Lorem ipsum.
"""
    out, err = run_pandoc_process(['--filter=panflute', '--to=html',
                                   f'--metadata=panflute-path:{EXAMPLES / "panflute"}'], md, filter_env)
    assert 'Hello world!' in err
    # caps: upper-case text; headers: one level deeper
    assert '<h2 id="level-1">LEVEL 1</h2>' in out
    assert '<h3 id="level-2">LEVEL 2</h3>' in out
    assert '<p>LOREM IPSUM.</p>' in out


@pytest.mark.requires_pandoc
def test_panfl_pipeline(filter_env):
    """pandoc -t json | panfl -t markdown filter | pandoc -f json"""
    json_doc, _ = run_pandoc_process(['--to=json'], '$1-1$', filter_env)
    proc = subprocess.run(['panfl', '-t', 'markdown', '-d', str(PANFL / 'bar'), 'test_filter'],
                          input=json_doc, capture_output=True, text=True, env=filter_env)
    assert proc.returncode == 0, proc.stderr
    out, _ = run_pandoc_process(['--from=json', '--to=markdown'], proc.stdout, filter_env)
    assert out == '$1+1markdown$'


def test_dump_text_helper_matches_stdio():
    text = doc_json()
    assert run_stdio(None, [], False, False, input_text=text) == dump_text(load_text(text))
