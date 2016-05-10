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

def build_cmds(fn):
    pandoc_path = which('pandoc')
    input_fn = './input/' + os.path.splitext(fn)[0] + '-sample.md'
    cmds = []
    for path in ('pandocfilters', 'panflute'):
        filter_fn = './{}/{}'.format(path, fn)
        cmds.append([pandoc_path, '-F', filter_fn, input_fn])
    return cmds

def main():
    print('Verify that the panflute filters are the same as'
          'those in pandocfilters.py:')

    pandoc_filters = os.listdir('./pandocfilters')
    panflute_filters = os.listdir('./panflute')
    excluded = ('abc.py', 'plantuml.py', 'tikz')

    for fn in pandoc_filters:
        if fn in panflute_filters and not fn.startswith('__') and not fn in excluded:
            print(' - Testing', fn)
            benchmark_cmd, panflute_cmd = build_cmds(fn)
            
            print('   [CMD]', ' '.join(benchmark_cmd))
            benchmark = shell(benchmark_cmd).decode('utf-8')
            print('   [CMD]', ' '.join(panflute_cmd))
            panflute = shell(panflute_cmd).decode('utf-8')

            print('   are both files the same?')
            print('   ... length?', len(benchmark) == len(panflute),
                  len(benchmark), len(panflute))
            print('   ... content?', benchmark == panflute)

            if benchmark != panflute:
                with open('benchmark_output.html', encoding='utf-8', mode='w') as f:
                    f.write(benchmark)
                with open('panflute_output.html', encoding='utf-8', mode='w') as f:
                    f.write(panflute)

                print('\n\n!!! Not equal.. check why!\n')
                if fn not in ('metavars.py',):
                    raise Exception

            print()


if __name__ == '__main__':
    main()


