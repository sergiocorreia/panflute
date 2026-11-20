# Panflute test suite

## Running the tests

Install panflute with its development dependencies (from the root of the repo:
`python -m pip install -e ".[dev,extras]"`, see
[CONTRIBUTING.md](../CONTRIBUTING.md#development-setup)) and run:

```
pytest                                   # from the repository root, or
pytest /path/to/panflute/tests           # from anywhere else
pytest --cov --cov-report=html           # with coverage (report in htmlcov/)
```

- The suite does not depend on the working directory: every file is located
  relative to `tests/`.
- Tests that need a `pandoc` executable are marked `requires_pandoc` and are
  *skipped* when pandoc is not on the `PATH`; everything else runs anywhere.
  Run only the pandoc-free part with `pytest -m "not requires_pandoc"`.
- Tests in which pandoc runs panflute filters (`pandoc --filter panfl`,
  `pandoc --filter some_filter.py`) use the `filter_env` fixture, which puts the
  directory of the running interpreter (`Path(sys.executable).parent`, where
  `python`, `panflute` and `panfl` are installed) first on the `PATH` of the
  subprocess. You do not need to activate the virtual environment.
- The suite does not inherit `PANDOC_VERSION` or `PANDOC_READER_OPTIONS` from
  the caller's environment: an autouse fixture (`no_pandoc_environment` in
  `conftest.py`) removes them for every test. Filters run by pandoc still
  receive them from pandoc.
- Warnings: deprecation warnings raised from panflute's own code are errors
  (see `filterwarnings` in `pyproject.toml`).

The whole suite takes about 10 seconds.

## Layout

| File | What it covers |
|------|----------------|
| `conftest.py` | `requires_pandoc` skipping, `no_pandoc_environment` (autouse), `filter_env` and `clean_import_state` fixtures |
| `helpers.py` | paths to the fixtures, JSON load/dump helpers |
| `test_golden.py` | characterisation tests on the stored pandoc JSON fixtures (no pandoc needed): `load`→`dump` reproduces pandoc's JSON, no-op walks/filters change nothing, the walk order and the output of `stringify()` / `get_metadata()` are pinned |
| `test_pandoc_roundtrip.py` | the same round trip through the *installed* pandoc (whatever its version): pandoc reads panflute's output back to the same document |
| `test_elements.py` | every element class: construction, exact `to_json()` output, JSON round trip, equality, defaults, type checking of children |
| `test_containers.py` | `ListContainer` / `DictContainer` |
| `test_walk.py` | navigation (`parent`, `next`, `prev`, `offset`, `ancestor`, `container`, `doc`), `walk()` semantics, `run_filters` on a `Doc`, `replace_keyword` |
| `test_tables.py` | `Table` and its parts |
| `test_io.py` | `load`, `dump`, `run_filter(s)`, `toJSONFilter(s)`, pandoc environment variables |
| `test_tools.py` | `stringify`, `yaml_filter`, metadata helpers, `get_option`, `convert_text`, `run_pandoc`, `shell`, `PandocVersion` |
| `test_autofilter.py` | the `panflute`/`panfl` CLIs, `stdio()`, filter search |
| `test_utils.py` | `panflute.utils`, and the list of public names |
| `test_lazy_imports.py` | `click` and `yaml` are imported on first use, invisibly: attributes, `dir()`, star imports, console scripts, pickling (in fresh interpreters) |
| `test_examples.py` | the example filters in `examples/panflute` run through pandoc |
| `test_regressions.py` | regression tests for specific issues |
| `type_checking/sample_filter.py` | not a test module: a sample filter that `mypy` checks (see `[tool.mypy]` in `pyproject.toml`), with `assert_type()` checks on the types users see |
| `benchmark.py` | not a test module: performance benchmarks (see [Benchmarks](#benchmarks)) |

### Known bugs: strict `xfail` tests

Tests marked `@pytest.mark.xfail(strict=True, reason="...")` (kept in
`test_regressions.py`; there are none at the moment) describe the **correct** behaviour for a known bug that
is not fixed yet. When a fix makes one of them pass, pytest reports it as a
failure (`XPASS(strict)`): remove the marker, and keep the test as a regression
test.

## Fixtures

```
fixtures/
  corpus/           hand-written sources covering every element type
                    (Markdown, HTML tables, and a pandoc "native" kitchen sink)
  sample_files/     older sample documents (Markdown and native)
  json/             pandoc's JSON output for all of the above (generated)
  benchmarks/       three large real-world documents (.md) and their JSON (generated);
                    see benchmarks/README.md
  goldens/          outputs of panflute itself, pinning current behaviour (generated)
  filters/          small filters run by pandoc in test_io.py
  panfl/            filters (a module and a package) used by test_autofilter.py
  dependency/       module imported by test_utils.py
  regenerate.py     regenerates json/, benchmarks/*.json and goldens/
```

The files in `fixtures/` are not collected by pytest (`collect_ignore_glob` in
`conftest.py`), even when named `test_*.py`.

### Regenerating the fixtures

The JSON fixtures are stored so that the golden tests run without pandoc. They
are pandoc's output, byte for byte; the pandoc version that produced them is
recorded in `fixtures/json/PANDOC_VERSION`. To regenerate them after adding or
editing a source file (with pandoc on the `PATH`):

```
python tests/fixtures/regenerate.py
```

Then regenerate the panflute goldens, which depend on the JSON fixtures:

```
python tests/fixtures/regenerate.py --panflute
```

The goldens (`fixtures/goldens/`) record what *panflute* currently does (walk
order, `stringify()` and `get_metadata()` output). Regenerate them only when a
change in behaviour is intended, and review the diff.

To add a document to the corpus, put it in `fixtures/corpus/` (`.md` files are
picked up automatically; other formats need an entry in `sources()` in
`regenerate.py`), then regenerate both sets of fixtures.

## Benchmarks

`benchmark.py` (not collected by pytest) times what a filter process spends
its time on: `import panflute`, `load`, a no-op and a transforming `walk`,
`stringify`, `dump`, and a no-op filter run end to end (as pandoc runs it),
on a small document and on the three documents in `fixtures/benchmarks/`.
It reports the minimum over several runs, in milliseconds:

```
python tests/benchmark.py                 # takes about a minute
python tests/benchmark.py --quick         # fewer runs
```

To measure a change, compare against another version of panflute, extracted
to a directory outside the repository; the two are run in alternation, so
that both see the same machine noise:

```
mkdir /tmp/panflute-master
git archive master panflute | tar -x -C /tmp/panflute-master
python tests/benchmark.py --compare /tmp/panflute-master
```

Differences of a few percent are within the noise.
