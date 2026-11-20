"""
Regression tests for specific issues.

Tests marked ``xfail(strict=True)`` describe the *correct* behaviour for a
known bug that is not fixed yet: they fail today, and the suite will report
an unexpected pass (XPASS -> failure) as soon as the bug is fixed, so that
the marker gets removed. Unmarked tests guard bugs that are already fixed.
"""

import importlib.util
import io
import json
import sys
import time
import warnings

import pytest

import panflute as pf
import panflute.tools as tools
from panflute.autofilter import autorun_filters

from .helpers import EXAMPLES, load_text, to_json_value

pytestmark = pytest.mark.usefixtures('clean_import_state')


def load_example(name, monkeypatch):
    """Import examples/panflute/<name>.py as a module, without writing bytecode."""
    monkeypatch.setattr(sys, 'dont_write_bytecode', True)
    path = EXAMPLES / 'panflute' / f'{name}.py'
    spec = importlib.util.spec_from_file_location(f'panflute_example_{name.replace("-", "_")}', path)
    module = importlib.util.module_from_spec(spec)
    with warnings.catch_warnings():
        warnings.simplefilter('error', SyntaxWarning)  # e.g. invalid escape sequences
        spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Fixed issues
# ---------------------------------------------------------------------------

def test_quotes_129():
    # https://github.com/sergiocorreia/panflute/issues/129
    para = pf.Para(pf.Quoted(pf.Str('Some'), pf.Space, pf.Str('quoted text')))
    assert pf.stringify(para, False) == '"Some quoted text"'


def test_index_223():
    """Index values on duplicated elements must be their actual position
    (they used to be computed with list.index(), which finds the first match)."""
    # https://github.com/sergiocorreia/panflute/issues/223
    doc = pf.Doc(pf.Para(pf.Str('a')), pf.Para(pf.Str('b')),
                 pf.Para(pf.Str('a')), pf.Para(pf.Str('c')))
    for index, element in enumerate(doc.content):
        assert element.index == index


def test_metadata_subclassed_builtins_166():
    # https://github.com/sergiocorreia/panflute/issues/166
    class MyDict(dict):
        pass
    doc = pf.Doc(metadata=MyDict(a=MyDict(b=[1])))
    assert doc.get_metadata('a.b') == ['1']


def test_parent_set_without_accessing_the_container_255():
    # https://github.com/sergiocorreia/panflute/issues/255 (first part: fixed)
    s = pf.Str('x')
    p = pf.Para(s)
    assert s.parent is p and s.index == 0
    t = pf.Str('y')
    p.content.append(t)
    assert t.parent is p and t.index == 1
    u = pf.Str('z')
    p.content[0] = u
    assert u.parent is p and u.index == 0
    m = pf.MetaString('v')
    mm = pf.MetaMap()
    mm['k'] = m
    assert m.parent is mm


@pytest.mark.parametrize('version', [[1, 22], [1, 22, 1], [1, 23], [1, 23, 1], [1, 23, 1, 1]])
def test_api_versions_246_248(version):
    # https://github.com/sergiocorreia/panflute/issues/246
    # https://github.com/sergiocorreia/panflute/issues/248
    text = '{"pandoc-api-version":%s,"meta":{},"blocks":[]}' % version
    doc = load_text(text)
    assert list(doc.api_version) == version
    assert to_json_value(doc)['pandoc-api-version'] == version


def test_too_old_api_version_is_rejected_246():
    with pytest.raises(TypeError, match='invalid api version'):
        load_text('{"pandoc-api-version":[1,20],"meta":{},"blocks":[]}')


@pytest.mark.parametrize('version,expected', [
    ([1, 20], r'invalid api version 1\.20: panflute requires pandoc API version 1\.22 or later \(pandoc 2\.11'),
    ([1, 23, 1, 0, 0], r'invalid api version 1\.23\.1\.0\.0: panflute requires'),
    ([], r'invalid api version \(empty\): panflute requires'),
    (['1', '23'], r"invalid api version \['1', '23'\]: expected a sequence of integers"),
])
def test_invalid_api_version_message_explains_the_problem_246(version, expected):
    text = '{"pandoc-api-version":%s,"meta":{},"blocks":[]}' % json.dumps(version)
    with pytest.raises(TypeError, match=expected) as info:
        load_text(text)
    assert len(info.value.args) == 1        # a message, not a tuple of values


# ---------------------------------------------------------------------------
# Bugs fixed in 3.0 (these tests were strict xfails before the fixes)
# ---------------------------------------------------------------------------

def test_convert_text_does_not_mutate_extra_args_262(monkeypatch):
    calls = []
    monkeypatch.setattr(tools, 'run_pandoc', lambda text, args, pandoc_path=None: calls.append(args) or '')
    args = ['--katex']
    pf.convert_text('x', output_format='html', extra_args=args, standalone=True)
    pf.convert_text('x', output_format='html', extra_args=args, standalone=False)
    assert args == ['--katex']
    assert calls[1] == ['--from=markdown', '--to=html', '--katex']


@pytest.mark.parametrize('fmt', ['comment', 'asciidoc', 'html5', 'beamer', 'my-custom-writer'])
def test_raw_elements_accept_any_format_236_247(fmt):
    assert pf.RawInline('x', format=fmt).format == fmt
    assert pf.RawBlock('x', format=fmt).format == fmt


def test_load_document_with_comment_raw_block_247():
    text = ('{"pandoc-api-version":[1,23,1],"meta":{},"blocks":[{"t":"RawBlock","c":["comment","hidden"]},'
            '{"t":"Para","c":[{"t":"RawInline","c":["comment","x"]}]}]}')
    doc = load_text(text)
    assert doc.content[0].format == 'comment'
    assert to_json_value(doc) == json.loads(text)


@pytest.mark.parametrize('fmt', [1, None, b'html'])
def test_raw_elements_still_reject_non_strings(fmt):
    with pytest.raises(TypeError):
        pf.RawInline('x', format=fmt)
    with pytest.raises(TypeError):
        pf.RawBlock('x', format=fmt)
    assert 'html' in pf.elements.RAW_FORMATS


def test_sibling_navigation_after_insert_255():
    a, b = pf.Str('a'), pf.Str('b')
    p = pf.Para(a, b)
    p.content.insert(0, pf.Str('new'))
    assert b.index == 2
    assert b.next is None          # currently b.next is b itself
    assert a.prev.text == 'new'


def test_sibling_navigation_after_delete_255():
    p = pf.Para(pf.Str('x'), pf.Str('y'), pf.Str('z'))
    y, z = p.content[1], p.content[2]
    del p.content[0]
    assert z.index == 1
    assert y.prev is None          # currently y.prev is y itself
    assert z.next is None


def test_navigation_after_negative_indexing():
    p = pf.Para(pf.Str('a'), pf.Str('b'), pf.Str('c'))
    last = p.content[-1]
    assert last.index == 2
    assert last.next is None       # currently Str(a)
    assert last.prev.text == 'b'   # currently None


def test_listcontainer_insert_negative_index():
    p = pf.Para(pf.Str('a'), pf.Str('b'))
    v = pf.Str('v')
    p.content.insert(-1, v)
    # (check before iterating over p.content, which re-attaches every element)
    assert v.parent is p           # currently None: the last element is attached instead
    assert v.index == 1
    assert p.content.list[-1].index == 2
    assert [e.text for e in p.content.list] == ['a', 'v', 'b']


def test_listcontainer_insert_past_the_end():
    p = pf.Para(pf.Str('a'))
    w = pf.Str('w')
    p.content.insert(5, w)         # list.insert() semantics: append
    assert w.parent is p and w.index == 1
    assert [e.text for e in p.content.list] == ['a', 'w']


def test_listcontainer_slicing_does_not_change_original_indexes():
    p = pf.Para(pf.Str('a'), pf.Str('b'), pf.Str('c'))
    b, c = p.content[1], p.content[2]
    p.content[1:3]
    assert b.index == 1            # currently 0
    assert b.prev.text == 'a'      # currently None
    assert c.next is None          # currently Str(c) itself


def test_listcontainer_slice_assignment():
    p = pf.Para(pf.Str('a'), pf.Str('b'), pf.Str('c'))
    new = [pf.Str('x'), pf.Str('y')]
    p.content[0:2] = new
    assert all(e.parent is p for e in new)
    assert [e.index for e in new] == [0, 1]
    assert [e.text for e in p.content.list] == ['x', 'y', 'c']


def test_listcontainer_slice_assignment_shifts_and_extended_slices():
    p = pf.Para(pf.Str('a'), pf.Str('b'), pf.Str('c'))
    c = p.content.list[2]
    x, y, z = pf.Str('x'), pf.Str('y'), pf.Str('z')
    p.content[0:1] = [x, y, z]     # more elements than replaced: 'c' moves
    assert [e.index for e in (x, y, z)] == [0, 1, 2]
    assert c.index == 4 and c.prev.text == 'b' and c.next is None
    p.content[::2] = [pf.Str('0'), pf.Str('2'), pf.Str('4')]
    assert [e.index for e in p.content.list] == [0, 1, 2, 3, 4]
    assert [e.text for e in p.content.list] == ['0', 'y', '2', 'b', '4']
    p.content[1:3] = []
    assert [(e.text, e.index) for e in p.content.list] == [('0', 0), ('b', 1), ('4', 2)]
    with pytest.raises(ValueError):  # extended slices must keep the length
        p.content[::2] = [pf.Str('q')]
    assert len(p.content) == 3


def test_listcontainer_delete_and_insert_with_negative_indexes():
    p = pf.Para(pf.Str('a'), pf.Str('b'), pf.Str('c'), pf.Str('d'))
    d = p.content.list[3]
    del p.content[-3]
    assert d.index == 2 and d.prev.text == 'c'
    p.content.insert(-10, pf.Str('first'))   # clipped, like list.insert()
    assert [(e.text, e.index) for e in p.content.list] == [('first', 0), ('a', 1), ('c', 2), ('d', 3)]
    p.content[-1] = new = pf.Str('D')
    assert new.parent is p and new.index == 3 and new.prev.text == 'c'
    assert p.content.pop(-2).text == 'c'
    assert new.index == 2 and new.prev.text == 'a'


def test_listcontainer_slices_do_not_change_elements():
    p = pf.Para(pf.Str('a'), pf.Str('b'), pf.Str('c'))
    elements = list(p.content.list)
    sl = p.content[1:]
    assert [e.text for e in sl] == ['b', 'c']     # iterating over the slice
    assert sl[0] is elements[1] and sl[-1] is elements[2] and sl[::-1][0] is elements[2]
    sl.walk(lambda e, doc: None)
    for index, e in enumerate(elements):
        assert (e.parent, e.location, e.index) == (p, None, index)
    sl.insert(0, pf.Str('x'))                     # changing the slice does not change p
    sl[1] = pf.Str('y')
    del sl[-1]
    assert [e.text for e in p.content] == ['a', 'b', 'c']
    assert [e.text for e in sl] == ['x', 'y']
    with pytest.raises(TypeError):
        sl[0] = pf.Para()


def test_element_in_two_containers_reports_the_last_one_accessed():
    s = pf.Str('shared')
    p1 = pf.Para(pf.Str('a'), s)
    p2 = pf.Para(s)
    assert s.parent is p2 and s.index == 0      # placed last in p2
    assert p1.content[1] is s and s.parent is p1 and s.index == 1
    p2.content.insert(0, pf.Str('b'))           # s is not attached to p2 now: left as it is
    assert s.parent is p1 and s.index == 1
    assert p2.content[1] is s and s.parent is p2 and s.index == 1


def test_metamap_content_setter_accepts_mappings_and_pairs():
    source = pf.MetaMap(a=pf.MetaString('x'))
    for value in (source.content, source, [('a', pf.MetaString('x'))], {'a': pf.MetaString('x')}.items()):
        mm = pf.MetaMap()
        mm.content = value
        assert list(mm) == ['a'] and mm['a'] == pf.MetaString('x') and mm['a'].parent is mm


def test_metalist_slice_assignment_attaches_items_260():
    ml = pf.MetaList('a', 'b', 'c')
    ml[1:] = [{'k': 'v'}]
    assert len(ml) == 2 and isinstance(ml[1], pf.MetaMap)
    assert ml.content.list[1].parent is ml and ml.content.list[1].index == 1


def test_listcontainer_slice_assignment_type_checked():
    p = pf.Para(pf.Str('a'))
    with pytest.raises(TypeError):
        p.content[0:1] = [pf.Para()]
    assert p.content[0].text == 'a'


def test_metalist_slice_assignment_260():
    ml = pf.MetaList('a', 'b', 'c')
    ml[0:2] = ['x', True]
    assert ml[0] == pf.MetaString('x')
    assert ml[1] == pf.MetaBool(True)
    assert len(ml) == 3


def test_metalist_slice_read_and_delete_260():
    ml = pf.MetaList('a', 'b', 'c')
    assert [m.text for m in ml[0:2]] == ['a', 'b']
    del ml[0:2]
    assert [m.text for m in ml] == ['c']


def test_metamap_content_setter_accepts_dict():
    mm = pf.MetaMap()
    mm.content = {'a': pf.MetaString('x')}
    assert mm['a'] == pf.MetaString('x')
    assert mm['a'].parent is mm


@pytest.mark.parametrize('other', [None, 1, 'x', []])
def test_listcontainer_comparison_with_other_types(other):
    lc = pf.Para(pf.Str('a')).content
    assert (lc == other) is False
    assert (lc != other) is True


def test_yaml_filter_no_deprecation_warning():
    calls = []
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        pf.yaml_filter(pf.CodeBlock('a: 1\n---\ndata', classes=['t']), None, tag='t',
                       function=lambda **kw: calls.append(kw))
        pf.yaml_filter(pf.CodeBlock('---\na: 1\n---\ndata', classes=['t']), None, tag='t',
                       function=lambda **kw: calls.append(kw), strict_yaml=True)
    assert [(c['options'], c['data']) for c in calls] == [({'a': 1}, 'data'), ({'a': 1}, 'data')]
    assert [w for w in caught if issubclass(w.category, DeprecationWarning)] == []


@pytest.mark.parametrize('text', [
    '---\n- a\n- b\n---\ndata',           # a list
    '---\njust a string\n---\ndata',       # a scalar
])
def test_yaml_filter_strict_with_non_mapping_yaml(text, capsys):
    calls = []
    elem = pf.CodeBlock(text, classes=['t'])
    result = pf.yaml_filter(elem, None, tag='t', function=lambda **kw: calls.append(kw), strict_yaml=True)
    assert result is None and calls == []      # left unchanged, like malformed YAML
    assert 'not a mapping' in capsys.readouterr().err


def test_yaml_filter_strict_with_empty_or_unparsable_yaml(capsys):
    calls = []
    f = lambda **kw: calls.append(kw)
    pf.yaml_filter(pf.CodeBlock('---\n# only a comment\n---\ndata', classes=['t']), None,
                   tag='t', function=f, strict_yaml=True)
    assert [(c['options'], c['data']) for c in calls] == [({}, 'data')]
    assert pf.yaml_filter(pf.CodeBlock('---\na: [1\n---\ndata', classes=['t']), None,
                          tag='t', function=f, strict_yaml=True) is None
    assert len(calls) == 1 and 'malformed YAML' in capsys.readouterr().err


def test_pandoc_version_runs_pandoc_once(monkeypatch):
    calls = []
    monkeypatch.setattr(tools, 'run_pandoc', lambda *a, **k: calls.append(a) or 'pandoc 3.1.3\n')
    v = tools.PandocVersion()
    assert v.version == (3, 1, 3)
    assert str(v) == '3.1.3'
    assert v.version == (3, 1, 3)
    assert len(calls) == 1


@pytest.mark.skipif(sys.platform == 'win32', reason='POSIX-only bug')
def test_shell_without_waiting(tmp_path):
    marker = tmp_path / 'done'
    code = f'import pathlib; print("not to our stdout"); pathlib.Path({str(marker)!r}).write_text("x")'
    assert pf.shell([sys.executable, '-c', code], wait=False) is None
    for _ in range(200):
        if marker.exists():
            break
        time.sleep(0.05)
    assert marker.read_text() == 'x'


@pytest.mark.parametrize('kwargs', [{'rowspan': 1.5}, {'colspan': 2.0}])
def test_table_cell_spans_must_be_int(kwargs):
    with pytest.raises(TypeError):
        pf.TableCell(**kwargs)


def test_autorun_filters_restores_previous_stdout(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'dont_write_bytecode', True)
    monkeypatch.setattr(sys, '__stdout__', io.StringIO())  # never touch the real one
    (tmp_path / 'noop_filter_xyz.py').write_text('def main(doc):\n    pass\n')
    mine = io.StringIO()
    monkeypatch.setattr(sys, 'stdout', mine)
    autorun_filters(['noop_filter_xyz'], pf.Doc(), [str(tmp_path)], False)
    assert sys.stdout is mine


def test_autorun_filters_restores_stdout_on_error(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'dont_write_bytecode', True)
    monkeypatch.setattr(sys, '__stdout__', io.StringIO())
    (tmp_path / 'failing_filter_xyz.py').write_text('def main(doc):\n    raise RuntimeError("x")\n')
    mine = io.StringIO()
    monkeypatch.setattr(sys, 'stdout', mine)
    with pytest.raises(Exception):
        autorun_filters(['failing_filter_xyz'], pf.Doc(), [str(tmp_path)], False)
    assert sys.stdout is mine


def test_context_import_restores_sys_path_on_import_error(tmp_path):
    from panflute.utils import ContextImport
    path_before = list(sys.path)
    with pytest.raises(ImportError):
        with ContextImport('panflute_no_such_module_xyz', str(tmp_path)):
            pass
    assert sys.path == path_before


def test_panfl_no_sys_path_option(monkeypatch):
    import panflute.autofilter as autofilter
    calls = []
    monkeypatch.setattr(autofilter, 'stdio', lambda *args, **kwargs: calls.append(args))
    monkeypatch.setattr(sys, 'argv', list(sys.argv))
    pf.panfl.main(['f', '-t', 'html', '--no-sys-path'], standalone_mode=False)
    pf.panfl.main(['f', '-t', 'html'], standalone_mode=False)
    assert [c[3] for c in calls] == [False, True]


def test_autorun_filters_warning_is_a_message_not_a_tuple(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, 'dont_write_bytecode', True)
    (tmp_path / 'noisy_filter_xyz.py').write_text('def main(doc):\n    print("noise")\n')
    autorun_filters(['noisy_filter_xyz'], pf.Doc(), [str(tmp_path)], False)
    err = capsys.readouterr().err
    assert 'Panflute Warning: filter "noisy_filter_xyz" wrote to stdout, but Pandoc does not allow that' in err
    assert "('Panflute" not in err


@pytest.mark.parametrize('kwargs', [{'rowspan': True}, {'colspan': 2}])
def test_table_cell_spans_accept_ints(kwargs):
    cell = pf.TableCell(**kwargs)
    assert cell.to_json()[2:4] == [kwargs.get('rowspan', 1), kwargs.get('colspan', 1)]


def test_citation_default_prefix_and_suffix():
    c = pf.Citation('id')
    assert len(c.prefix) == 0 and len(c.suffix) == 0
    assert c.to_json()['citationPrefix'] == [] and c.to_json()['citationSuffix'] == []


def test_dump_to_stdout_does_not_replace_sys_stdout(monkeypatch):
    buffer = io.BytesIO()
    stream = io.TextIOWrapper(buffer, encoding='latin-1', newline='\r\n')
    monkeypatch.setattr(sys, 'stdout', stream)
    print('before')
    pf.dump(pf.Doc(pf.Para(pf.Str('h\u00e9llo \u2603')), api_version=(1, 23, 1)))
    assert sys.stdout is stream and not stream.closed
    print('after')
    stream.flush()
    expected = ('{"pandoc-api-version":[1,23,1],"meta":{},"blocks":[{"t":"Para","c":'
                '[{"t":"Str","c":"h\u00e9llo \u2603"}]}]}')
    assert buffer.getvalue() == b'before\r\n' + expected.encode('utf-8') + b'after\r\n'


def test_dump_to_stdout_without_buffer(monkeypatch):
    out = io.StringIO()               # e.g. contextlib.redirect_stdout(), or pytest's capsys
    monkeypatch.setattr(sys, 'stdout', out)
    pf.dump(pf.Doc(api_version=(1, 23, 1)))
    assert sys.stdout is out
    assert out.getvalue() == '{"pandoc-api-version":[1,23,1],"meta":{},"blocks":[]}'


def test_load_from_stdin_does_not_close_it(monkeypatch):
    text = '{"pandoc-api-version":[1,23,1],"meta":{},"blocks":[{"t":"Para","c":[{"t":"Str","c":"\u00e9"}]}]}'
    stdin = io.TextIOWrapper(io.BytesIO(text.encode('utf-8')), encoding='ascii')
    monkeypatch.setattr(sys, 'stdin', stdin)
    doc = pf.load()
    import gc
    gc.collect()
    assert doc.content[0].content[0].text == '\u00e9'
    assert sys.stdin is stdin and not stdin.buffer.closed


def test_load_from_stdin_without_buffer(monkeypatch):
    monkeypatch.setattr(sys, 'stdin', io.StringIO('{"pandoc-api-version":[1,23,1],"meta":{},"blocks":[]}'))
    assert pf.load() == pf.Doc()


@pytest.mark.parametrize('arg', ['--help', '-h', '--version'])
def test_panflute_command_help_and_version(arg, monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['panflute', arg])
    monkeypatch.setattr(sys, 'stdin', io.StringIO(''))   # would fail if it were read
    pf.main()
    out = capsys.readouterr().out
    assert ('Usage: panflute' in out) if arg != '--version' else (out == f'panflute {pf.__version__}\n')


# ---------------------------------------------------------------------------
# Example filters (examples/panflute) that used to be broken
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('elem,expected', [
    (pf.Code('score.ly', classes=['ly']), pf.RawInline('\\includely[staffsize=20]{score.ly}', format='latex')),
    (pf.CodeBlock("{ c' }", classes=['ly']), pf.RawBlock("\\lily[staffsize=20]{{ c' }}", format='latex')),
])
def test_example_lilypond_latex(monkeypatch, elem, expected):
    module = load_example('lilypond', monkeypatch)
    assert module.lily(elem, pf.Doc(format='latex')) == expected


def test_example_myemph_latex(monkeypatch):
    module = load_example('myemph', monkeypatch)
    span = module.myemph(pf.Emph(pf.Str('x')), pf.Doc(format='latex'))
    assert pf.stringify(span) == '\\myemph{x}'


def test_example_table(monkeypatch):
    module = load_example('table', monkeypatch)
    table = pf.Table(pf.TableBody(pf.TableRow(pf.TableCell(pf.Plain(pf.Str('41'))))))
    module.add_one(table, pf.Doc())
    assert pf.stringify(table) == '42'
    # all the rows: table head, intermediate heads, bodies and foot
    row = lambda text: pf.TableRow(pf.TableCell(pf.Plain(pf.Str(text))))
    table = pf.Table(pf.TableBody(row('1'), head=[row('2')]), head=pf.TableHead(row('3')),
                     foot=pf.TableFoot(row('x')))
    module.add_one(table, pf.Doc())
    assert pf.stringify(table) == '423x'   # (stringify order: head, body rows, intermediate head, foot)


@pytest.mark.parametrize('name', ['metavars', 'myemph'])
def test_examples_have_no_invalid_escapes(name):
    path = EXAMPLES / 'panflute' / f'{name}.py'
    with warnings.catch_warnings():
        warnings.simplefilter('error', SyntaxWarning)
        compile(path.read_text(encoding='utf-8'), str(path), 'exec')


def test_example_table_better(monkeypatch):
    module = load_example('table-better', monkeypatch)
    cell = pf.TableCell(pf.Plain(pf.Str('41')))
    module.add_one(cell, pf.Doc())
    assert pf.stringify(cell) == '42'
