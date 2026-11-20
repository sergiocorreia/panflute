"""
Run the example filters in examples/panflute/ through pandoc and check that
they do what they claim. Examples that need external programs (abcm2ps,
gregorio, graphviz, lilypond, LaTeX) are not run here; some of them are
unit-tested in test_regressions.py.
"""

import re
import subprocess

import pytest

from .helpers import EXAMPLES, PANDOC

pytestmark = pytest.mark.requires_pandoc

FILTERS = EXAMPLES / 'panflute'
INPUTS = EXAMPLES / 'input'


def normalise_markers(markdown):
    """
    Collapse the spaces after list and definition markers ('-   x' -> '- x'):
    their number depends on pandoc's version (3.1.13 writes '-   x', 3.6.4
    writes '- x').
    """
    return re.sub(r'^([ \t]*(?:[-*+:~]|\d+[.)]))[ \t]+', r'\1 ', markdown, flags=re.MULTILINE)


def run_example(name, env, cwd, to='markdown', input_name=None):
    source = INPUTS / (input_name or f'{name}-sample.md')
    proc = subprocess.run([PANDOC, f'--filter={FILTERS / name}.py', f'--to={to}', str(source)],
                          capture_output=True, text=True, env=env, cwd=cwd)
    assert proc.returncode == 0, proc.stderr
    return proc.stdout


def run_plain(name, cwd, to='markdown', input_name=None):
    source = INPUTS / (input_name or f'{name}-sample.md')
    proc = subprocess.run([PANDOC, f'--to={to}', str(source)], capture_output=True, text=True, cwd=cwd)
    assert proc.returncode == 0, proc.stderr
    return proc.stdout


@pytest.fixture
def run(filter_env, tmp_path):
    # Run in a temporary directory: some filters write files to the cwd
    def _run(name, **kwargs):
        return run_example(name, filter_env, tmp_path, **kwargs)
    return _run


def test_caps(run):
    assert run('caps').strip() == 'THIS IS THE CAPS SAMPLE WITH LOREM.'


def test_headers(run, tmp_path):
    out = run('headers', input_name='headers.md')
    assert out.startswith('## A level 1 header\n')
    assert '###### Level 5' in out
    assert run_plain('headers', tmp_path, input_name='headers.md').startswith('# A level 1 header\n')


def test_deemph(run):
    assert 'This is EMPHASIS WITH UNICODE REMOVED text' in run('deemph').replace('\n', ' ')


def test_deflists(run, tmp_path):
    out = normalise_markers(run('deflists'))
    assert '- **Term 1**' in out
    assert 'Definition 1' in out
    assert ': Definition 1' not in out
    assert ': Definition 1' in normalise_markers(run_plain('deflists', tmp_path))


def test_comments(run, tmp_path):
    out = run('comments')
    assert 'This is a comment' not in out
    assert 'This is regular text again.' in out
    assert 'This is a comment' in run_plain('comments', tmp_path)


def test_metavars(run):
    assert run('metavars').strip() == '# Caleb Hyde {#author}'


def test_theorem_latex(run):
    out = run('theorem', to='latex')
    assert '\\begin{theorem}' in out and '\\end{theorem}' in out


def test_theorem_other_formats_unchanged(run, tmp_path):
    assert run('theorem') == run_plain('theorem', tmp_path)


def test_build_table(run):
    out = run('build-table')
    assert ': This table should not have a header' in out
    assert 'Quality' in out and 'Memo' in out
    assert '``` table_without_header' not in out


def test_tikz_non_latex_raw_blocks_untouched(run, tmp_path):
    assert run('tikz') == run_plain('tikz', tmp_path)
