"""
Regenerate the stored pandoc JSON fixtures used by the golden tests.

Usage (from anywhere; paths are resolved relative to this file):

    python tests/fixtures/regenerate.py                # pandoc JSON fixtures
    python tests/fixtures/regenerate.py --panflute     # panflute goldens (see below)

The JSON files under ``json/`` and ``benchmarks/`` are produced by *pandoc*
(not by panflute) from the sources listed in ``SOURCES`` below, so the tests
that compare panflute's output with them never need pandoc at test time.
They were last generated with the pandoc version recorded in
``json/PANDOC_VERSION``; regenerating with another pandoc version may change
them (e.g. a different ``pandoc-api-version``), which is expected.

The files under ``goldens/`` are different: they are generated *by panflute*
from the JSON fixtures, and pin its current behaviour:

- ``walk-kitchen_sink.txt``: the order (and tree depth) in which
  ``Element.walk`` visits the elements of ``json/kitchen_sink.json``;
- ``stringify.json``: ``stringify(doc)`` and ``stringify(doc, newlines=False)``
  for every JSON fixture;
- ``metadata.json``: ``doc.get_metadata()`` for every JSON fixture.

Only regenerate them (``--panflute``) when a change of behaviour is intended,
and review the diff.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / 'corpus'
SAMPLES = HERE / 'sample_files'
JSON_DIR = HERE / 'json'
BENCH_DIR = HERE / 'benchmarks'
GOLDEN_DIR = HERE / 'goldens'


def sources():
    """Yield (source file, output file, extra pandoc args)."""
    for md in sorted(CORPUS.glob('*.md')):
        yield md, JSON_DIR / f'{md.stem}.json', ['--from=markdown']
    yield (CORPUS / 'metadata.md', JSON_DIR / 'metadata-cli.json',
           ['--from=markdown', '--metadata=cli-string:from the command line',
            '--metadata=cli-flag'])
    yield (CORPUS / 'citations.md', JSON_DIR / 'citations-citeproc.json',
           ['--from=markdown', '--citeproc',
            f'--bibliography={CORPUS / "citations.bib"}'])
    yield CORPUS / 'tables.html', JSON_DIR / 'tables-html.json', ['--from=html']
    yield (CORPUS / 'kitchen_sink.native', JSON_DIR / 'kitchen_sink.json',
           ['--from=native'])
    for md in sorted(SAMPLES.glob('*/example.md')):
        yield md, JSON_DIR / f'sample-{md.parent.name}.json', ['--from=markdown']
    for native in sorted((SAMPLES / 'native').glob('*.native')):
        yield native, JSON_DIR / f'native-{native.stem}.json', ['--from=native']
    for md in sorted(BENCH_DIR.glob('*.md')):
        if md.name == 'README.md':
            continue
        yield md, BENCH_DIR / f'{md.stem}.json', ['--from=markdown']


def run_pandoc(source, args):
    cmd = ['pandoc', *args, '--to=json', str(source)]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return proc.stdout.decode('utf-8')


def regenerate_json():
    JSON_DIR.mkdir(exist_ok=True)
    version = subprocess.run(['pandoc', '--version'], capture_output=True,
                             check=True, text=True).stdout.splitlines()[0]
    (JSON_DIR / 'PANDOC_VERSION').write_text(version + '\n', encoding='utf-8')
    for source, target, args in sources():
        text = run_pandoc(source, args)
        json.loads(text)  # sanity check
        # Store pandoc's output byte for byte (no trailing newline added)
        target.write_bytes(text.encode('utf-8'))
        print(f'{target.relative_to(HERE)}  <-  {source.relative_to(HERE)} {" ".join(args)}')


def walk_order(doc):
    """List of 'depth tag' strings, in the order walk() calls the action."""
    def depth(elem):
        d = 0
        while elem.parent is not None:
            elem = elem.parent
            d += 1
        return d

    visited = []

    def action(elem, doc):
        visited.append(f'{depth(elem)} {elem.tag}')

    doc.walk(action)
    return visited


def load(path):
    import panflute as pf
    with open(path, encoding='utf-8') as f:
        return pf.load(f)


def write_json(path, data):
    text = json.dumps(data, indent=1, ensure_ascii=False, sort_keys=True)
    path.write_text(text + '\n', encoding='utf-8')


def regenerate_panflute_goldens():
    import panflute as pf
    GOLDEN_DIR.mkdir(exist_ok=True)
    lines = walk_order(load(JSON_DIR / 'kitchen_sink.json'))
    (GOLDEN_DIR / 'walk-kitchen_sink.txt').write_text('\n'.join(lines) + '\n',
                                                      encoding='utf-8')
    print(f'goldens/walk-kitchen_sink.txt ({len(lines)} visits)')

    stringified = {}
    metadata = {}
    for path in sorted(JSON_DIR.glob('*.json')):
        stringified[path.name] = {
            'newlines': pf.stringify(load(path)),
            'no_newlines': pf.stringify(load(path), newlines=False),
        }
        metadata[path.name] = load(path).get_metadata()
    write_json(GOLDEN_DIR / 'stringify.json', stringified)
    write_json(GOLDEN_DIR / 'metadata.json', metadata)
    print('goldens/stringify.json, goldens/metadata.json')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--panflute', action='store_true',
                        help='regenerate the panflute goldens instead of the pandoc JSON')
    args = parser.parse_args(argv)
    if args.panflute:
        regenerate_panflute_goldens()
    else:
        regenerate_json()


if __name__ == '__main__':
    sys.exit(main())
