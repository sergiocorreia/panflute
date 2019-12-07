import os
import sys
from shutil import which
from subprocess import Popen, PIPE, call


def shell(args, msg=None):
    # Fix Windows error if passed a string
    proc = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate(input=msg)
    exitcode = proc.returncode
    if exitcode!=0:
        print('\n------', file=sys.stderr)
        print(err.decode('utf-8'), file=sys.stderr, end='')
        print('------\n', file=sys.stderr)
        raise IOError
    return out


def build_cmd(fn):
    pandoc_path = which('pandoc')
    input_fn = './examples/input/' + os.path.splitext(fn)[0] + '-sample.md'
    filter_fn = './examples/{}/{}'.format('panflute', fn)
    return [pandoc_path, '-F', filter_fn, input_fn]


def test_filters_run():
    print('Verify that all panflute actually filters run')
    panflute_filters = os.listdir('./examples/panflute')

    # GABC, etc requires installing miktex packages...
    excluded = ['abc.py', 'plantuml.py', 'tikz', 'gabc.py', 'graphviz.py']
    
    # Lilypond, etc. have bugs
    excluded.extend(['lilypond.py'])

    # These have no "**-sample.md" file
    excluded.extend(['headers.py', 'table-better.py', 'table.py'])

    for fn in panflute_filters:
        if not fn.startswith('__') and fn not in excluded:
            print(' - Testing', fn)
            panflute_cmd = build_cmd(fn)

            print('   [CMD]', ' '.join(panflute_cmd))
            panflute = shell(panflute_cmd).decode('utf-8')
            print()


if __name__ == '__main__':
    test_filters_run()
