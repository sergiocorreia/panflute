# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# noinspection PyProtectedMember
from panflute import _get_filter_dir
import subprocess
from subprocess import PIPE
import os.path as p
import os

os.chdir(p.dirname(p.dirname(__file__)))

in1 = '$1-1$'
out1 = '$1+1markdown$'
out1a = 'panflute: data_dir={} sys_path={}'

in2 = '$1∕1$'
out2 = r'$\frac{1}{1}$'


def test_all():
    assert _get_filter_dir() == _get_filter_dir(hardcoded=True)

    def run_proc(*args, stdin):
        proc = subprocess.run(args, stdout=PIPE, stderr=PIPE, input=stdin,
                              encoding='utf-8', cwd=os.getcwd())
        _stdout, _stderr = proc.stdout, proc.stderr
        return (_stdout if _stdout else '').strip(), (_stderr if _stderr else '').strip()

    _in, _out = [in1], [out1]

    def template1(*extra_args):
        _stdout = run_proc('pandoc', '-t', 'json', stdin=_in[0])[0]
        _stdout = run_proc('panfl', '-t', 'markdown', *extra_args, stdin=_stdout)[0]
        _stdout = run_proc('pandoc', '-f', 'json', '-t', 'markdown', stdin=_stdout)[0]
        return _stdout == _out[0]

    assert template1('-d', './tests/test_panfl', 'test_filter/test_filter.py')
    assert template1(p.abspath('./tests/test_panfl/test_filter/test_filter.py'))
    assert template1('-d', './tests/test_panfl', 'test_filter.test_filter')
    assert template1('-d', './tests/test_panfl', 'test_filter')

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
    assert out1a.format(False, False) in stderr

    def template2(*extra_args, dd, sp):
        _stdout = run_proc('pandoc', '-t', 'json',
                           '--metadata', 'panflute-verbose: True',
                           stdin=in1)[0]
        _stderr = run_proc('panfl', '-t', 'markdown', '-d', './tests/test_panfl',
                           p.abspath('./tests/test_panfl/__filter__.py'),
                           *extra_args, stdin=_stdout)[1]  # __filter__.py doesn't exist
        return out1a.format(dd, sp) in _stderr

    assert template2('--data-dir', '--no-sys-path', dd=True, sp=False)
    assert template2('--no-sys-path', dd=False, sp=False)

    def ver_tuple(v):
        return tuple(map(int, (v.split('+')[0].split('.')[0:3])))

    try:
        import sugartex
        if ver_tuple(sugartex.__version__) >= (0, 1, 12):
            _in[0], _out[0] = in2, out2
            assert template1('sugartex')
    except ModuleNotFoundError:
        pass

# test_all()
# print(0, file=open(r'D:\log.txt', 'a', encoding='utf-8'))
