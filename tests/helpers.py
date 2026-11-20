"""
Paths and helper functions shared by the test modules.
"""

import io
import json
import shutil
import sys
from pathlib import Path

import panflute as pf


TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent
FIXTURES = TESTS_DIR / 'fixtures'
JSON_FIXTURES = FIXTURES / 'json'
BENCHMARKS = FIXTURES / 'benchmarks'
CORPUS = FIXTURES / 'corpus'
SAMPLE_FILES = FIXTURES / 'sample_files'
FILTERS = FIXTURES / 'filters'
EXAMPLES = REPO_ROOT / 'examples'

PANDOC = shutil.which('pandoc')
SCRIPTS_DIR = Path(sys.executable).parent


def json_fixture_paths():
    return sorted(JSON_FIXTURES.glob('*.json'))


def benchmark_paths():
    return sorted(BENCHMARKS.glob('*.json'))


def read_text(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def load_text(text):
    """Load a JSON string into a Doc."""
    return pf.load(io.StringIO(text))


def load_path(path):
    with open(path, encoding='utf-8') as f:
        return pf.load(f)


def dump_text(doc):
    """Dump a Doc into a JSON string."""
    with io.StringIO() as f:
        pf.dump(doc, f)
        return f.getvalue()


def to_json_value(elem):
    """Fully serialise an element (or Doc) into plain JSON values."""
    return json.loads(json.dumps(elem, default=lambda e: e.to_json()))


def roundtrip(elem):
    """Element -> JSON -> Element, through panflute's own JSON decoder."""
    from panflute.elements import from_json
    text = json.dumps(elem, default=lambda e: e.to_json())
    return json.loads(text, object_hook=from_json)


# Order in which panflute emits the keys of a Citation object (pandoc uses a
# different order, which may also vary across pandoc versions).
PANFLUTE_CITATION_KEYS = ('citationSuffix', 'citationNoteNum', 'citationMode',
                          'citationPrefix', 'citationId', 'citationHash')


def canonical_pandoc_json(text):
    """
    Re-serialise pandoc's JSON output the way panflute serialises JSON:
    compact separators, no ASCII escaping, and Citation keys in panflute's
    order. Everything else (key order, number formatting, escapes) is taken
    from pandoc's output as is.
    """
    def hook(dct):
        if 'citationId' in dct:
            assert set(dct) == set(PANFLUTE_CITATION_KEYS)
            return {k: dct[k] for k in PANFLUTE_CITATION_KEYS}
        return dct

    data = json.loads(text, object_hook=hook)
    return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
