"""
Benchmarks for panflute (not collected by pytest, not part of the package).

Measures what a pandoc filter spends its time on:

    import    ``python -c "import panflute"`` (wall time of a fresh process,
              minus that of ``python -c pass``)
    load      JSON text -> Doc (``pf.load`` from a ``StringIO``)
    walk      no-op walk (``doc.walk(lambda e, d: None)``)
    xwalk     transforming walk (replace elements, return lists, delete with [],
              change elements in place)
    stringify ``pf.stringify(doc)``
    dump      Doc -> JSON text (``pf.dump`` into a ``StringIO``)
    e2e       wall time of a no-op filter process (``pf.run_filter``) reading a
              document from stdin and writing it to stdout, as pandoc runs it

Every number is the minimum over several runs (in milliseconds).

Usage (from the repository root):

    python tests/benchmark.py                  # the panflute that `import panflute` finds
    python tests/benchmark.py --compare DIR    # also DIR/panflute (e.g. an older version,
                                               #   from `git archive <rev> panflute | tar -x -C DIR`),
                                               #   with the two measured in alternation
    python tests/benchmark.py --quick          # fewer runs
    python tests/benchmark.py --docs portugal  # a subset of the documents
"""

import argparse
import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
BENCHMARKS = TESTS_DIR / 'fixtures' / 'benchmarks'
SMALL_DOC = TESTS_DIR / 'fixtures' / 'json' / 'sample-example1.json'
DOCS = {'small': SMALL_DOC, **{p.stem: p for p in sorted(BENCHMARKS.glob('*.json'))}}

E2E_FILTER = "import panflute as pf\npf.run_filter(lambda elem, doc: None)\n"


# ---------------------------
# In-process measurements (worker)
# ---------------------------

def _transform(elem, doc):
    # A bit of everything that filters do
    pf = _transform.pf
    if isinstance(elem, pf.Str):
        if 'a' in elem.text:
            return pf.Str(elem.text.upper())        # replace
        if 'e' in elem.text:
            elem.text = elem.text + '!'               # change in place
    elif isinstance(elem, pf.Emph):
        return list(elem.content)                     # unwrap: return a list
    elif isinstance(elem, pf.SoftBreak):
        return []                                     # delete
    elif isinstance(elem, pf.Link):
        elem.url = elem.url.replace('http:', 'https:')
    elif isinstance(elem, pf.Header):
        return [elem, pf.Para(pf.Str('after'), pf.Space, pf.Str('header'))]


def _min_time(func, setup, repeat):
    best = float('inf')
    for _ in range(repeat):
        arg = setup()
        t0 = time.perf_counter()
        func(arg)
        best = min(best, time.perf_counter() - t0)
    return best * 1000


def worker(names, repeat):
    import panflute as pf
    _transform.pf = pf
    results = {}
    for name in names:
        text = DOCS[name].read_text(encoding='utf-8')
        load = lambda: pf.load(io.StringIO(text))  # noqa: E731
        r = {}
        r['load'] = _min_time(lambda t: pf.load(io.StringIO(t)), lambda: text, repeat)
        r['walk'] = _min_time(lambda d: d.walk(lambda e, doc: None), load, repeat)
        r['xwalk'] = _min_time(lambda d: d.walk(_transform), load, repeat)
        doc = load()
        r['stringify'] = _min_time(pf.stringify, lambda: doc, repeat)
        r['dump'] = _min_time(lambda d: pf.dump(d, io.StringIO()), lambda: doc, repeat)
        results[name] = r
    return results


# ---------------------------
# Subprocess measurements
# ---------------------------

# Subprocesses run in BENCHMARKS, so that `python -c ...` (which puts the current
# directory first in sys.path) doesn't import the panflute of the current directory

def _env(pythonpath):
    env = dict(os.environ)
    env.pop('PANDOC_VERSION', None)
    env.pop('PANDOC_READER_OPTIONS', None)
    if pythonpath:
        env['PYTHONPATH'] = pythonpath
    return env


def _wall(args, env, stdin=None):
    t0 = time.perf_counter()
    subprocess.run(args, env=env, input=stdin, stdout=subprocess.DEVNULL, check=True, cwd=BENCHMARKS)
    return (time.perf_counter() - t0) * 1000


def measure_process(pythonpath, names):
    """One wall-time sample of each subprocess benchmark (ms)."""
    env = _env(pythonpath)
    py = sys.executable
    out = {'python': _wall([py, '-c', 'pass'], env),
           'import': _wall([py, '-c', 'import panflute'], env)}
    for name in names:
        data = DOCS[name].read_bytes()
        out['e2e:' + name] = _wall([py, '-c', E2E_FILTER, 'html'], env, stdin=data)
    return out


def importtime(pythonpath):
    """Cumulative import time of panflute reported by -X importtime (us)."""
    proc = subprocess.run([sys.executable, '-X', 'importtime', '-c', 'import panflute'],
                          env=_env(pythonpath), capture_output=True, text=True, check=True,
                          cwd=BENCHMARKS)
    for line in proc.stderr.splitlines():
        parts = [x.strip() for x in line.split('|')]
        if len(parts) == 3 and parts[2] == 'panflute':
            return int(parts[1])
    return None


def measure_worker(pythonpath, names, repeat):
    proc = subprocess.run([sys.executable, __file__, '--worker', '--repeat', str(repeat),
                           '--docs', *names],
                          env=_env(pythonpath), capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


# ---------------------------
# Driver
# ---------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--compare', metavar='DIR',
                        help='directory containing another panflute package to compare against')
    parser.add_argument('--docs', nargs='+', choices=sorted(DOCS), default=sorted(DOCS))
    parser.add_argument('--rounds', type=int, default=5,
                        help='worker processes per variant (default: 5)')
    parser.add_argument('--repeat', type=int, default=5,
                        help='runs of each in-process benchmark per worker (default: 5)')
    parser.add_argument('--quick', action='store_true', help='--rounds 2 --repeat 3')
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.worker:
        json.dump(worker(args.docs, args.repeat), sys.stdout)
        return
    if args.quick:
        args.rounds, args.repeat = 2, 3

    variants = {'current': ''}
    if args.compare:
        variants = {'other': str(Path(args.compare).resolve()), 'current': ''}

    best = {v: {} for v in variants}

    def keep_min(v, key, value):
        if value is not None:
            best[v][key] = min(best[v].get(key, float('inf')), value)

    # Alternate between the variants, so that both see the same machine noise
    for _ in range(args.rounds):
        for v, path in variants.items():
            for doc, r in measure_worker(path, args.docs, args.repeat).items():
                for k, value in r.items():
                    keep_min(v, f'{k}:{doc}', value)
            for _ in range(3):
                for k, value in measure_process(path, ['small', 'portugal']).items():
                    keep_min(v, k, value)
            it = importtime(path)
            keep_min(v, 'importtime', it / 1000 if it is not None else None)

    for v in variants:
        best[v]['import'] = best[v]['import'] - best[v]['python']

    keys = sorted(best['current'], key=lambda k: (k.split(':')[-1], k))
    print(f'Python {sys.version.split()[0]}; minimum over runs, in ms')
    if args.compare:
        print(f'{"benchmark":<24}{"other":>10}{"current":>10}{"change":>9}')
        for k in keys:
            a, b = best['other'][k], best['current'][k]
            print(f'{k:<24}{a:>10.1f}{b:>10.1f}{(b - a) / a:>+9.0%}')
    else:
        for k in keys:
            print(f'{k:<24}{best["current"][k]:>10.1f}')


if __name__ == '__main__':
    main()
