"""
`import panflute` does not import click (needed only by the command line
interfaces in panflute.autofilter) nor yaml (needed only by yaml_filter):
they are imported the first time they are used (module ``__getattr__``).

These tests check that this is invisible: the names are still attributes of
their modules, listed by dir(), bound by star imports, and usable by the
console scripts and by pickle. Each test runs in a fresh interpreter.
"""

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

import panflute as pf

from .helpers import FIXTURES


def python(args, **kwargs):
    """Run a fresh interpreter, which imports the same panflute as the tests."""
    env = dict(os.environ)
    env['PYTHONPATH'] = os.pathsep.join(
        [str(Path(pf.__file__).parent.parent)] + env.get('PYTHONPATH', '').split(os.pathsep))
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          cwd=FIXTURES, env=env, **kwargs)


def run_python(code, *args):
    """Run code in a fresh interpreter and return what it printed as JSON."""
    proc = python(['-c', textwrap.dedent(code), *args])
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


AUTOFILTER_NAMES = ['get_filter_dirs', 'main', 'panfl', 'stdio']
YAML_NAMES = ['Loader', 'yaml', 'yamlloader']

# Everything `from panflute import *` binds (the package has no __all__)
PANFLUTE_STAR_NAMES = {
    'BlockQuote', 'Block', 'BulletList', 'Caption', 'Citation', 'Cite', 'Code', 'CodeBlock',
    'Definition', 'DefinitionItem', 'DefinitionList', 'DictContainer', 'Div', 'Doc', 'Element',
    'Emph', 'Figure', 'Header', 'HorizontalRule', 'Image', 'Inline', 'LineBlock', 'LineBreak',
    'LineItem', 'Link', 'ListContainer', 'ListItem', 'Math', 'MetaBlocks', 'MetaBool',
    'MetaInlines', 'MetaList', 'MetaMap', 'MetaString', 'MetaValue', 'Note', 'Null',
    'OrderedList', 'Para', 'Plain', 'Quoted', 'RawBlock', 'RawInline', 'SmallCaps', 'SoftBreak',
    'Space', 'Span', 'Str', 'Strikeout', 'Strong', 'Subscript', 'Superscript', 'Table',
    'TableBody', 'TableCell', 'TableFoot', 'TableHead', 'TableRow', 'Underline',
    'autofilter', 'base', 'containers', 'convert_text', 'debug', 'dump', 'elements',
    'get_filter_dirs', 'get_option', 'io', 'load', 'main', 'panfl', 'run_filter', 'run_filters',
    'run_pandoc', 'shell', 'stdio', 'stringify', 'table_elements', 'toJSONFilter',
    'toJSONFilters', 'tools', 'utils', 'version', 'yaml_filter',
}


def test_import_panflute_does_not_import_click_or_yaml():
    loaded = run_python("""
        import json, sys
        import panflute
        print(json.dumps([m for m in ('click', 'yaml', 'yamlloader', 'panflute.autofilter')
                          if m in sys.modules]))
    """)
    assert loaded == []


def test_lazy_names_are_attributes():
    res = run_python("""
        import json, sys
        import panflute as pf
        import panflute.tools
        import click, yaml
        try:
            import yamlloader
            loader = yamlloader.ordereddict.CSafeLoader
        except ImportError:
            yamlloader = None
            loader = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)
        from panflute import autofilter
        print(json.dumps({
            'autofilter': pf.autofilter is sys.modules['panflute.autofilter'] is autofilter,
            'functions': [getattr(pf, n) is getattr(autofilter, n) for n in
                          ('main', 'panfl', 'stdio', 'get_filter_dirs')],
            'panfl': isinstance(pf.panfl, click.Command),
            'yaml': [pf.tools.yaml is yaml, pf.tools.yamlloader is yamlloader,
                     pf.tools.Loader is loader],
            'hasattr': [hasattr(pf, 'panfl'), hasattr(pf.tools, 'Loader')],
            # once looked up, the names are in the module namespaces, as before
            'vars': [n in vars(pf) for n in ('main', 'panfl', 'stdio', 'get_filter_dirs', 'autofilter')]
                    + [n in vars(pf.tools) for n in ('yaml', 'yamlloader', 'Loader')],
        }))
    """)
    assert res == {'autofilter': True, 'functions': [True] * 4, 'panfl': True,
                   'yaml': [True] * 3, 'hasattr': [True] * 2, 'vars': [True] * 8}


def test_unknown_attributes_raise_attribute_error():
    res = run_python("""
        import json
        import panflute, panflute.tools
        out = []
        for mod in (panflute, panflute.tools):
            try:
                mod.does_not_exist
            except AttributeError as e:
                out.append(str(e))
            out.append(hasattr(mod, '__all__'))
        print(json.dumps(out))
    """)
    assert res == ["module 'panflute' has no attribute 'does_not_exist'", False,
                   "module 'panflute.tools' has no attribute 'does_not_exist'", False]


def test_dir_lists_the_lazy_names_before_they_are_imported():
    res = run_python("""
        import json, sys
        import panflute, panflute.tools
        d1, d2 = dir(panflute), dir(panflute.tools)
        print(json.dumps({'panflute': d1, 'tools': d2, 'sorted': [d1 == sorted(d1), d2 == sorted(d2)],
                          'loaded': [m for m in ('click', 'yaml') if m in sys.modules]}))
    """)
    assert set(AUTOFILTER_NAMES + ['autofilter']) <= set(res['panflute'])
    assert set(YAML_NAMES) <= set(res['tools'])
    assert res['sorted'] == [True, True]
    assert res['loaded'] == []


def test_star_import_panflute():
    res = run_python("""
        import json
        ns = {}
        exec('from panflute import *', ns)
        import panflute
        print(json.dumps({
            'names': sorted(n for n in ns if n != '__builtins__'),
            'public': sorted(n for n in vars(panflute) if not n.startswith('_')),
            'same': all(ns[n] is getattr(panflute, n) for n in ns if n != '__builtins__'),
        }))
    """)
    assert set(res['names']) == PANFLUTE_STAR_NAMES
    assert res['names'] == res['public']
    assert res['same']


def test_star_import_panflute_tools():
    res = run_python("""
        import json
        ns = {}
        exec('from panflute.tools import *', ns)
        import panflute.tools as tools
        print(json.dumps({
            'names': sorted(n for n in ns if n != '__builtins__'),
            'public': sorted(n for n in vars(tools) if not n.startswith('_')),
            'same': all(ns[n] is getattr(tools, n) for n in ns if n != '__builtins__'),
        }))
    """)
    assert set(YAML_NAMES) <= set(res['names'])
    assert {'stringify', 'yaml_filter', 'Para', 'json', 'annotations'} <= set(res['names'])
    assert res['names'] == res['public']
    assert res['same']


def test_console_script_entry_points():
    res = run_python("""
        import json
        from importlib.metadata import entry_points
        import panflute
        eps = {ep.name: ep for ep in entry_points(group='console_scripts')
               if ep.value.startswith('panflute:')}
        print(json.dumps({name: [ep.value, ep.load() is getattr(panflute, ep.attr)] for name, ep in eps.items()}))
    """)
    if not res:
        pytest.skip('panflute is not installed')
    assert res == {'panflute': ['panflute:main', True], 'panfl': ['panflute:panfl', True]}


@pytest.mark.parametrize('args, expected', [
    (['-c', 'from panflute import main; import sys; sys.argv[1:] = ["--version"]; main()'], 'panflute '),
    (['-c', 'from panflute import panfl; panfl(["--help"])'], 'Usage:'),
    (['-m', 'panflute.autofilter'], ''),
])
def test_command_line_interfaces(args, expected):
    proc = python(args, stdin=subprocess.DEVNULL)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.startswith(expected)


def test_pickle_by_reference():
    res = run_python("""
        import json, pickle, subprocess, sys
        import panflute as pf
        data = pickle.dumps([pf.main, pf.stdio, pf.get_filter_dirs, pf.tools.Loader, pf.stringify])
        code = ('import pickle, sys, panflute as pf; objs = pickle.loads(sys.stdin.buffer.read()); '
                'print(objs == [pf.main, pf.stdio, pf.get_filter_dirs, pf.tools.Loader, pf.stringify])')
        out = subprocess.run([sys.executable, '-c', code], input=data, capture_output=True, check=True)
        print(json.dumps(out.stdout.decode().strip()))
    """)
    assert res == 'True'


def test_filter_search_path_is_sys_path_at_import_time(tmp_path):
    # autofilter.reduced_sys_path is computed when panflute is imported, as
    # before, not when autofilter is first used
    res = run_python("""
        import json, sys
        import panflute
        sys.path.append(sys.argv[1])
        print(json.dumps(sys.argv[1] in panflute.autofilter.reduced_sys_path))
    """, str(tmp_path))
    assert res is False


def test_yaml_filter_uses_a_loader_set_by_the_user():
    # Setting panflute.tools.Loader before yaml is imported is respected
    res = run_python("""
        import json, yaml
        import panflute as pf
        pf.tools.Loader = yaml.BaseLoader  # every scalar is a string
        out = []
        doc = pf.Doc(pf.CodeBlock('a: 1\\n---\\ndata', classes=['tag']))
        pf.yaml_filter(doc.content[0], doc, tag='tag',
                       function=lambda options, data, element, doc: out.append(options))
        print(json.dumps(out))
    """)
    assert res == [{'a': '1'}]
