# Contributing to Panflute

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

This document contains useful resources and guidelines when contributing to the project:


#### Table Of Contents

- [Development setup](#development-setup)
- [Style guide](#style-guide)
- [Panflute internals](#panflute-internals)
- [Documentation](#documentation)


## Development setup

You need Python 3.10+ and [pandoc](https://pandoc.org/installing.html) on your `PATH`.
From a clone of the repository, create a virtual environment and install panflute in editable mode with the development tools:

```bash
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
python -m pip install -e ".[dev,extras]"
```

### Running the tests

Run the test suite (from the root of the repository, or pass the path to `tests/` from anywhere else):

```bash
pytest
```

Tests that need `pandoc` are skipped when it is not on the `PATH`. See [tests/README.md](tests/README.md) for how the suite is organized and how to regenerate its fixtures.

To also measure code coverage:

```bash
pytest --cov --cov-report=html   # report in htmlcov/index.html
```

### Linting and type checking

```bash
ruff check .
mypy
```

Both are configured in `pyproject.toml`. Please don't reformat code you are not otherwise changing.

Panflute ships inline type hints (and a `py.typed` marker). mypy checks the
`panflute` package, at a non-strict level, and also
`tests/type_checking/sample_filter.py`, a filter written the way a user would
write one, with `assert_type()` checks on the types that users see. If you
change a public signature, update that file too. Annotations must not affect
the behavior or speed of panflute, so they are not evaluated at runtime: each
module starts with `from __future__ import annotations`, and imports used only
in annotations go under `if TYPE_CHECKING:`. The code must keep working on
Python 3.10.

### Changelog

If your change is visible to users (a new feature, a bug fix, a change in behavior), add an entry for it to [CHANGELOG.md](CHANGELOG.md), in the matching section of the unreleased version at the top. Say first what changed for users, then give the issue or pull request number.

### Continuous integration

[GitHub Actions](https://github.com/sergiocorreia/panflute/blob/master/.github/workflows/run_tests.yml) runs ruff and mypy, the test suite (on several Python and pandoc versions), the example filters, the documentation build and a packaging check on every push to `master` and on every pull request.

## Style Guide

For consistency, code should try to comply (as much as possible) with [pep8](https://pypi.python.org/pypi/pep8), and with the style guides by [@kennethreitz](http://docs.python-guide.org/en/latest/writing/style/) and [Google](http://google.github.io/styleguide/pyguide.html).

### Useful tools

- [`pycodestyle`](https://pypi.org/project/pycodestyle/) (formerly `pep8`): run it with `pycodestyle ./panflute > pycodestyle-report.txt`
- [`pylint`](https://www.pylint.org/): run it with `pylint panflute > pylint-report.txt` from the root folder of the repo


## Panflute internals

Before proposing a speed-up, read [IDEAS.md](IDEAS.md): it lists changes that were considered for 3.0 and left out, most of them speed-ups, with their measurements and the reason each was left out.


### Program flow

- Filters usually call panflute with `panflute.run_filter(action)`.
  - Note: `run_filter`, `toJSONFilter` and `toJSONFilters` are just thin wrappers for `run_filters`.
- Within `run_filter`,
  1. `doc = panflute.load()` reads the JSON input from stdin and creates a `panflute.Doc` object, which is just a tree containing the entire document.
  2. `doc.walk(action, doc)` will walk through the document tree (top to bottom) and apply the `action` function
  3. `panflute.dump(doc)` will encode the tree into JSON and dump it to stdout, finishing execution


### Modules in the `panflute` package

- `__init__.py`: loads the functions that will be part of API of the package.
- `utils.py`: contains auxiliary functions that *do not* depend on any other part of `panflute`.
- `version.py`: has the version string.
- `containers.py`: has a `ListContainer` and `DictContainer` classes. These are just wrappers around lists and dicts, that i) allow only certain items of certain types to be added (through `.oktypes`), and ii) keep track of the parent objects to allow for navigation through the tree (so you can do `.parent`, `.prev`, `.next`, etc.).
  - Note: every element (and every container) also has a `.location` attribute, needed when the parent can hold more than one container. For instance, `Doc` holds both standard items in `.content` and metadata items in `.metadata`, so in order to traverse the tree, we need to know in which container of the parent each item is. `.location` is `None` for an item in the parent's `.content`, and otherwise the name of the parent's attribute that holds it (`'metadata'`, `'citations'`, `'caption'`, ...). It matters only for the children of `Doc`, `Cite`, `Citation`, `DefinitionItem`, `Figure`, `Table`, `TableBody` and `Caption`.
- `base.py`: has the base classes of all Pandoc elements. These are `Element` and its subclasses `Block`, `Inline` and `Metadata`.
- `elements.py` (and `table_elements.py`, for tables): have all the standard Pandoc elements (`Str`, `Para`, `Space`, etc.). Pandoc elements inherit from one of three base classes (`Block`, `Inline` and `Metadata`), which we use to make sure that an elements does not get placed in another element where it's not allowed.
  - Note: there are some elements not present in [pandoc-types](https://github.com/jgm/pandoc-types/blob/master/src/Text/Pandoc/Definition.hs) that are subclass from `Element` directly. These are `Doc`, `Citation`, `ListItem`, `Definition`, `DefinitionItem`, `TableCell` and `TableRow`. This allow filters to be applied directly to table rows instead of to tables and then looping within each item of the table.
  - `elements.py` also contains the function `from_json`, which is essential in converting JSON elements into Pandoc elements.
- `io.py`: holds all the I/O functions (`load`, `dump`, `run_filters`, and wrappers).
- `tools.py`: contain functions that are useful when writing filters (but not essential). These include `stringify`, `yaml_filter`, `convert_text`, etc.
  - Note: future enhancements to `panflute` should probably go here.
- `autofilter.py`: has the code that allows panflute to be run as an executable script.
  - This allows panflute to be run as a filter (!), in which case it uses the `panflute-...` metadata to conveniently call different filters.


## Documentation

Panflute uses [Sphinx](https://www.sphinx-doc.org/) for its documentation.
To build it, install panflute with the `docs` extra (Sphinx and myst-parser) and run Sphinx from the root of the repository:

```bash
python -m pip install -e ".[docs]"
sphinx-build -W -b html docs/source docs/build/html
```

Open `docs/build/html/index.html` to read the result; that folder is what is copied to the [website](https://scorreia.com/software/panflute/). `-W` turns warnings into errors, as in CI.

The guides are written in [reST](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html) and located in the [/docs/source](https://github.com/sergiocorreia/panflute/tree/master/docs/source) folder. The changelog page includes [CHANGELOG.md](CHANGELOG.md) (written in Markdown) from the root of the repository, so there is only one copy of it to update.

The API docs are written as comments in the [source code itself](https://github.com/sergiocorreia/panflute/blob/master/panflute/elements.py#L242) (so e.g. [this](http://scorreia.com/software/panflute/code.html) is autogenerated).

### REST guides

- [reST Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Sphinx commands](https://pythonhosted.org/an_example_pypi_project/sphinx.html)
- [Sphinx domains](https://www.sphinx-doc.org/en/master/usage/domains/python.html). This is used to create links to other python packages and to the stdlib (e.g. ``:py:data:`sys.stdin` ``, ``:mod:`sys` ``, ``:class:`zipfile.ZipFile` ``).
