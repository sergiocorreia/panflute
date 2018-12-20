# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import panflute as pf
import subprocess
from subprocess import PIPE
import os.path as p
import os
import sys
import io

os.chdir(p.dirname(p.dirname(__file__)))

in1 = '$1-1$'
out1 = '$1+1markdown$'
out1err = 'panflute: data_dir={dd} sys_path={sp}'
in1a = f"""---
panflute-filters: test_filter
panflute-path: ./tests/test_panfl
...
{}
""".format(in1)


def test_all():
    assert pf.get_filter_dir() == pf.get_filter_dir(hardcoded=False)

    def to_json(text):
        return pf.convert_text(text, 'markdown', 'json')

    def assert3(*extra_args, stdin):
        """
        filters=None, search_dirs=None, data_dir=True, sys_path=True, panfl_=False
        """
        sys.argv[1:] = []
        sys.argv.append('markdown')
        _stdout = io.StringIO()
        pf.stdio(*extra_args, input_stream=io.StringIO(stdin), output_stream=_stdout)
        _stdout = pf.convert_text(_stdout.getvalue(), 'json', 'markdown')
        assert _stdout == out1

    json1, json1a = to_json(in1), to_json(in1a)

    assert3(None, None, True, True, True, stdin=json1a)
    assert3(None, None, True, True, False, stdin=json1a)

    assert3(['test_filter/test_filter.py'], ['./tests/test_panfl'], False, True, True, stdin=json1)
    assert3([p.abspath('./tests/test_panfl/test_filter/test_filter.py')], [], False, True, True, stdin=json1)
    assert3(['test_filter.test_filter'], ['./tests/test_panfl'], False, True, True, stdin=json1)
    assert3(['test_filter'], ['./tests/test_panfl'], False, True, True, stdin=json1)

    # --------------------------------
    if sys.version_info[0:2] < (3, 6):
        return

    def run_proc(*args, stdin):
        proc = subprocess.run(args, stdout=PIPE, stderr=PIPE, input=stdin,
                              encoding='utf-8', cwd=os.getcwd())
        _stdout, _stderr = proc.stdout, proc.stderr
        return (_stdout if _stdout else '').strip(), (_stderr if _stderr else '').strip()

    def assert1(*extra_args):
        _stdout = run_proc('pandoc', '-t', 'json', stdin=in1)[0]
        _stdout = run_proc('panfl', '-t', 'markdown', *extra_args, stdin=_stdout)[0]
        _stdout = run_proc('pandoc', '-f', 'json', '-t', 'markdown', stdin=_stdout)[0]
        assert _stdout == out1

    # assert1('-d', './tests/test_panfl', 'test_filter/test_filter.py')
    # assert1(p.abspath('./tests/test_panfl/test_filter/test_filter.py'))
    # assert1('-d', './tests/test_panfl', 'test_filter.test_filter')
    assert1('-d', './tests/test_panfl', 'test_filter')

    stdout = run_proc('pandoc', '--filter', 'panfl', '-t', 'markdown',
                      '--metadata', 'panflute-filters: test_filter',
                      '--metadata', 'panflute-path: ./tests/test_panfl',
                      stdin=in1)[0]
    assert stdout == out1

    stderr = run_proc('pandoc', '--filter', 'panfl', '-t', 'markdown',
                      '--metadata', 'panflute-verbose: True',
                      '--metadata', 'panflute-filters: "{}"'.format(
                          p.abspath('./tests/test_panfl/__filter__.py')),
                      '--metadata', 'panflute-path: --no-sys-path',
                      stdin=in1)[1]  # __filter__.py doesn't exist
    assert out1err.format(dd=False, sp=False) in stderr

    def assert2(*extra_args, dd, sp):
        _stdout = run_proc('pandoc', '-t', 'json',
                           '--metadata', 'panflute-verbose: True',
                           stdin=in1)[0]
        _stderr = run_proc('panfl', '-t', 'markdown', '-d', './tests/test_panfl',
                           p.abspath('./tests/test_panfl/__filter__.py'),
                           *extra_args, stdin=_stdout)[1]  # __filter__.py doesn't exist
        assert out1err.format(dd=dd, sp=sp) in _stderr

    assert2('--data-dir', '--no-sys-path', dd=True, sp=False)
    assert2('--no-sys-path', dd=False, sp=False)


# test_all()
# print(0, file=open(r'D:\log.txt', 'a', encoding='utf-8'))
# with io.StringIO() as f:
#     pf.dump(doc, f)
#     out = f.getvalue()
