# Changelog

All notable changes to panflute are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Entries before 3.0.0 are brief; see the
[commit history](https://github.com/sergiocorreia/panflute/commits/master) for details.


## 3.0.0 (unreleased)

The first release since 2.3.1 (March 2024). It requires Python 3.10 or later,
ships type hints, accepts any raw format (such as `typst`, `comment` or
`latex-merge`), fixes many bugs in element navigation and containers, and
makes filters start and run faster. Most filters run unchanged: the
breaking changes below are the main incompatibilities (the "Changed" section
lists smaller differences in behavior), and the
[What's new in 3.0](https://scorreia.com/software/panflute/whatsnew.html)
page of the documentation explains how to migrate.

### Breaking changes

- **Python 3.10 or later is required** (2.3.1 supported Python 3.7 and later).
  Python 3.10 to 3.15 are supported, as is PyPy (tested with PyPy 3.11).
  *Migration:* on older Pythons, pip keeps installing panflute 2.3.1; if a
  project must keep working there, require `panflute<3` for those Pythons.
- **`MetaList.index` is now the sequence method** `index(value, start=0, stop=None)`,
  as on `list` ([#258](https://github.com/sergiocorreia/panflute/issues/258)).
  It used to be the position of the `MetaList` in its container, which made
  `metalist.index(value)` and `metalist.remove(value)` fail. The position of
  any element is now the new `Element.position` attribute; on every other
  element, `.index` remains a read/write alias of `.position`.
  *Migration:* replace `metalist.index` with `metalist.position` where it
  refers to a `MetaList` (beware that `if metalist.index is not None` is now
  always true, and that assigning to `metalist.index` raises `AttributeError`).
- **Pickles of a `MetaList` made with panflute 2.x cannot be loaded** by 3.0
  (`AttributeError`), nor can pickles of anything that contains one, such as
  a `Doc` whose metadata has a list. Other pickled elements still load.
  *Migration:* re-create the pickles with 3.0, or store documents as pandoc
  JSON (`dump()`/`load()`), which does not depend on the panflute version.
- **Slices of a `ListContainer`** (`elem.content[1:3]`) are now instances of
  a private subclass of `ListContainer`, so `type(s) is ListContainer` is
  false (`isinstance(s, ListContainer)` is still true). Reading, iterating or
  changing a slice no longer changes the `parent`/`position` of the elements
  (reading it used to re-index them relative to the slice). As before, a slice
  is a new container holding the same elements.
  *Migration:* use `isinstance()`, or `list(s)` for a plain list.
- **`TableCell` requires integer `rowspan` and `colspan`** and raises
  `TypeError` otherwise (a float used to be accepted and written into the
  JSON sent to pandoc). *Migration:* pass `int(...)`.

### Added

- **Type hints.** The public API is annotated inline and panflute ships a
  `py.typed` marker (PEP 561), so mypy, pyright and IDEs use them. If you
  installed a separate stub package, such as `panflute-stubs`, uninstall it:
  type checkers prefer it to the hints shipped with panflute. Filters that
  are already type-checked may see new errors where the hints are stricter
  (see the simplifications below). Enum-like arguments use `Literal`
  types (e.g. `Quoted(quote_type=...)`, `OrderedList(style=..., delimiter=...)`,
  `Math(format=...)`, `TableCell(alignment=...)`, `Citation(mode=...)`).
  Filter actions are typed `(Element, Doc) -> Element | list[Element] | None`,
  `walk()` returns the element or what the action returned for it, and
  `convert_text()` returns `list[Element]`, a `Doc` with `standalone=True`, or
  `Any` for other output formats. `MetaList` slicing is typed
  ([#260](https://github.com/sergiocorreia/panflute/issues/260)). (These hints
  build on an unreleased first version contributed in
  [#257](https://github.com/sergiocorreia/panflute/pull/257), thanks to Leilei332,
  and correct its `walk()` hints, [#259](https://github.com/sergiocorreia/panflute/issues/259);
  [castedo/panflute-stubs](https://github.com/castedo/panflute-stubs) was used as
  a reference.) Deliberate simplifications:
  - the `doc` passed to an action is typed `Doc`, although it is `None` when
    `walk()` is called on an element that is not part of a document;
  - `identifier`, `classes` and `attributes` are declared on every `Element`,
    although only elements with attributes have them;
  - passing a bare class (`Para(Space)`) instead of an instance
    (`Para(Space())`) still works at runtime but is rejected by type checkers.
- `Element.position`: the position of an element in the list container that
  holds it, or `None` when it is not in a list (e.g. a table caption, or a
  value of a `MetaMap`); see `MetaList.index` above.
- `panflute --help`, `panflute -h` and `panflute --version` print a short
  usage text or the version (they used to wait for a document on stdin).

### Changed

- Supported pandoc versions: 2.11.4 to 3.14, i.e. pandoc API 1.22 to
  1.23.1.x (2.3.1 was documented for pandoc up to 3.1); the table in the
  README says which versions are tested
  ([#248](https://github.com/sergiocorreia/panflute/issues/248)).
- `import panflute` no longer imports `click`, `yaml`/`yamlloader` or
  `panflute.autofilter`; they are imported the first time they are used
  (`yaml_filter()`, `panfl`, `panflute.autofilter`, ...). All names remain
  available as attributes, in `dir()` and through `from panflute import *`
  (which therefore still imports click and `panflute.autofilter`: use
  `import panflute as pf` to start faster). As a consequence, a missing or
  broken click or PyYAML installation is reported when it is first needed,
  not at import.
- `dump()` without an output stream writes the JSON as UTF-8 bytes to
  `sys.stdout.buffer`, or as text to `sys.stdout` when it has no buffer (e.g.
  an `io.StringIO` set by `contextlib.redirect_stdout` or by pytest's capture,
  where it used to raise `io.UnsupportedOperation`). It leaves `sys.stdout`
  alone: it used to replace it for good with a UTF-8 writer, so text printed
  to stdout *after* `dump()` now uses the stream's own encoding.
  Likewise, `load()` without an input stream no longer closes `sys.stdin.buffer`
  and works when `sys.stdin` is a text stream.
- `yaml_filter(..., strict_yaml=True)`: a YAML chunk that is not a mapping
  (a list or a scalar), or that fails to parse with a `yaml.parser.ParserError`,
  now prints a warning to stderr and leaves the code block unchanged, as YAML
  with a `yaml.scanner.ScannerError` already did, instead of raising
  `ValueError`, `TypeError` or `ParserError`. A chunk with only comments counts
  as no options.
- The "invalid api version" `TypeError` raised for documents from pandoc older
  than 2.11 now explains the problem and its usual cause (`convert_text()` and
  `run_pandoc()` run the first `pandoc` on the `PATH`, which can be older than
  the one running the filter). The exception is still a `TypeError` whose
  message starts with "invalid api version", but its `args` are now that
  single message (they used to be `('invalid api version', [1, 20])`)
  ([#246](https://github.com/sergiocorreia/panflute/issues/246)).
- `Citation`'s `prefix` and `suffix` default to `()` instead of `''` in its
  signature (same behavior; passing `''` still works).

### Fixed

- `RawBlock` and `RawInline` accept any format string, as pandoc does, so
  documents with e.g. `{=comment}`, `{=typst}`, `{=asciidoc}`, Quarto's
  `latex-merge` or custom-writer raw elements can be loaded and built
  ([#236](https://github.com/sergiocorreia/panflute/issues/236),
  [#247](https://github.com/sergiocorreia/panflute/issues/247); this
  generalizes unreleased fixes for `typst` and `latex-merge` from
  [#244](https://github.com/sergiocorreia/panflute/pull/244) and
  [#251](https://github.com/sergiocorreia/panflute/pull/251), thanks to jkub6 and
  matthew-brett). Other formats used to raise `TypeError`; non-string formats
  still do. `panflute.elements.RAW_FORMATS` is no longer used, and is kept
  only as a reference list.
- `convert_text(..., standalone=True, extra_args=args)` appended
  `'--standalone'` to the caller's `args` list, making later calls with the
  same list standalone too ([#262](https://github.com/sergiocorreia/panflute/issues/262)).
- An element's `parent` (and `position`, in a list) was only set when it was
  read back from its container: it is now set as soon as the element is added
  (when the parent is built, and by `append`, `insert`, item and slice
  assignment, and `MetaMap`/`DictContainer` item assignment)
  ([#255](https://github.com/sergiocorreia/panflute/issues/255),
  [#256](https://github.com/sergiocorreia/panflute/pull/256), thanks to me-kell).
- Element positions (`position`/`index`, and so `next`, `prev` and `offset()`)
  went stale or wrong: after `insert()` or `del` on a container, the elements
  after the change kept their old position (`b.next` could be `b` itself);
  reading with a negative index (`content[-1]`) stored a negative position;
  reading a slice re-indexed the original elements. Positions are now always non-negative and
  kept up to date by insertions, deletions and slice assignments.
- `MetaList.index(value)` and `MetaList.remove(value)` raised `TypeError`
  ([#258](https://github.com/sergiocorreia/panflute/issues/258); see
  "Breaking changes" above).
- Setting `MetaMap.content` to a `dict`, `MetaMap` or `DictContainer`
  raised `AttributeError`; it now accepts any mapping or iterable of pairs.
- Comparing a `ListContainer` with a non-container (`elem.content == 1`)
  raised `AttributeError`; it is now `False`.
- `yaml_filter` triggered a `DeprecationWarning` on Python 3.13+ (positional
  arguments to `re.split()`).
- `panflute.tools.pandoc_version` (a `PandocVersion`, used to find pandoc's
  data directory) never used its cache, running `pandoc --version` on every
  access to `.version`, `.data_dir` or `str()`.
- `shell(cmd, wait=False)` always raised `ValueError` on Linux and macOS. The
  command now runs detached, in its own session, with stdin and stdout
  redirected to `/dev/null` so that it cannot write into the document sent to
  pandoc (stderr is inherited; Windows is unchanged).
- `panfl --no-sys-path` had no effect with click 8.2 or later.
- When running filters listed in the metadata (`pandoc -F panflute`, `panfl`),
  panflute set `sys.stdout` to `sys.__stdout__` afterwards instead of
  restoring the previous stream, and left it redirected when a filter raised;
  its "filter wrote to stdout" warning was printed as a tuple.
- `ContextImport` left its directory on `sys.path` when the import failed.
- A docstring in `panflute.io` caused a `SyntaxWarning` (invalid escape
  sequence) on Python 3.12+ ([#264](https://github.com/sergiocorreia/panflute/pull/264), thanks to cdlm).
- Example filters: `lilypond.py` used undefined names, `myemph.py` and
  `table.py` used the `Element.items` attribute removed in panflute 2.0
  (`table.py` is rewritten for the current table model), `table-better.py`
  used undefined names, `graphviz.py` linked to the wrong image path, and
  `metavars.py` had invalid escape sequences.

### Performance

Measured with `tests/benchmark.py` on CPython 3.12, panflute 2.3.1 vs 3.0.0
(the minimum over several runs, on the same machine):

- `import panflute`: 82 ms → 22 ms. `from panflute import *` gains less,
  because it still imports click.
- A no-op filter run as pandoc runs it, on a small document: 107 ms → 45 ms.
- `walk()`: 36–42% faster when the action changes nothing, 27–37% faster
  when it replaces and deletes elements; `stringify()`: 27–35% faster.
- `load()` and `dump()`: unchanged.

### Packaging and infrastructure

- Built from `pyproject.toml` only (`setup.py` removed;
  [#250](https://github.com/sergiocorreia/panflute/pull/250), thanks to paddatrapper),
  with setuptools 77.0.3 or later and PEP 639 metadata: the license is the
  SPDX expression `BSD-3-Clause`.
- Extras: the `pypi` extra is removed; `dev` is now pytest, pytest-cov, ruff,
  mypy and types-PyYAML (configparser, coverage, flake8, pandocfilters and
  requests are dropped); a new `docs` extra installs what the documentation
  build needs; `extras` (yamlloader) is unchanged. The `requirements.txt` files
  are removed.
- The sdist includes `CHANGELOG.md`, `CONTRIBUTING.md`, the test suite and the
  example filters, so the tests can be run from it (pandoc required).
- New project URLs (documentation, repository, issues, changelog).
- Continuous integration rewritten: ruff and mypy; tests on Python 3.10–3.15
  and PyPy 3.11 against pandoc 2.11.4 up to the latest release; the example
  filters; a docs build; and a build check with `twine check --strict`.
- Releases are published to PyPI from GitHub Actions with Trusted Publishing,
  and the workflow refuses to publish when the release tag differs from the
  package version (see [#243](https://github.com/sergiocorreia/panflute/issues/243),
  [#252](https://github.com/sergiocorreia/panflute/issues/252)).
  `force-publish.yml` is removed; Dependabot keeps the actions up to date.
- The test suite was rebuilt: from 37 to 741 tests, with golden JSON
  round-trip fixtures and about 98% branch coverage.
- `tests/benchmark.py` times import, load, walk, stringify, dump and a whole
  filter run, optionally against another copy of panflute.
- The documentation was updated for 3.0, with a
  [What's new in 3.0](https://scorreia.com/software/panflute/whatsnew.html)
  page and this changelog.

### Known limitations (unchanged in 3.0.0)

- `stringify()` inserts the text of a footnote where the note is, with no
  separator ([#225](https://github.com/sergiocorreia/panflute/issues/225)).
- `Caption(short_caption=[])` is written as "no short caption" (`null`).
- `MetaMap(...) == {...}` is `False` (compare with `doc.get_metadata()` instead),
  and `Doc.__eq__` ignores `format` and `api_version`.
- An element removed from a container keeps its old `parent` and `position`;
  an element held by two containers (not counting slices) reports the one it
  was last added to or read from.


## 2.3.1 (2024-03-20)

- `MetaMap` and `MetaList` implement the `MutableMapping` and
  `MutableSequence` interfaces, converting built-in values to metadata elements
  ([#233](https://github.com/sergiocorreia/panflute/pull/233)).
- Fix a crash in `Figure.to_json()` and `Table.to_json()` when the caption is
  `None` ([#230](https://github.com/sergiocorreia/panflute/pull/230)).
- Drop support for Python 3.6.

## 2.3.0 (2023-01-26)

- Update the [Pandoc API](https://github.com/jgm/pandoc-types/blob/master/changelog)
  from 1.22 to 1.23 ([Pandoc 3.0](https://pandoc.org/releases.html#pandoc-3.0-2023-01-18)):
  - Add `Figure` block object
  - Remove `Null` block object (scheduled for removed)
