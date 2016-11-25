# Contributing to Panflute

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

This document contains useful resources and guidelines when contributing to the project:


#### Table Of Contents

- [Style guide](#style-guide)
- [Panflute internals](#panflute-internals)
- [Documentation](#documentation)


## Style Guide

For consistency, code should try to comply (as much as possible) with [pep8](https://pypi.python.org/pypi/pep8), and with the style guides by [@kennethreitz](http://docs.python-guide.org/en/latest/writing/style/) and [Google](http://google.github.io/styleguide/pyguide.html).


### Useful tools:

- [`pep8`](http://pep8.readthedocs.io/en/release-1.7.x/): run it with `pep8 > pep8-report.txt`
- [`pylint`](https://www.pylint.org/): run it with `pylint panflute > pylint-report.txt` from the root folder of the repo
pep8
- [Travis CI](https://travis-ci.org/sergiocorreia/panflute). Gets run automatically after pushing code to Github. Settings can be [customized](https://github.com/sergiocorreia/panflute/blob/master/.travis.yml), but it basically runs all files in [`\tests`](https://github.com/sergiocorreia/panflute/tree/master/tests) that fit the pattern `test_*.py`.


## Panflute internals


### Program flow

- Filters usually call panflute with `panflute.run_filter(action)`.
  - Note: `run_filter`, `toJSONFilter` and `toJSONFilters` are just thin wrappers for `run_filters`.
- Within `run_filter`,
  1. `doc = panflute.load()` reads the JSON input from stdin and creates a `panflute.Doc` object, which is just a tree containing the entire document.
  2. `doc.walk(action, doc)` will walk through the document tree (top to bottom) and apply the `action` function
  3. `panflute.dump(doc)` will encode the tree into JSON and dump it to stdout, finishing execution


## Modules in the `panflute` package

- `__init__.py`: loads the functions that will be part of API of the package.
- `utils.py`: contains auxiliary functions that *do not* depend on any other part of `panflute`.
- `version.py`: has the version string.
- `containers.py`: has a `ListContainer` and `DictContainer` classes. These are just wrappers around lists and ordered dicts, that i) allow only certain items of certain types to be added (through `.oktypes`), and ii) keep track of the parent objects to allow for navigation through the tree (so you can do `.parent`, `.prev`, `.next`, etc.).
  - Note: there is also a rarely used `._container` property, needed for when the parent object can hold more than one container. For instance, `Doc` holds both standard items in `.content` and also metadata items in `.metadata`, so in order to traverse the tree, we need to know in what container of the parent each item is. This is only used by the `Doc`, `Citation`, `DefinitionItem`, `Quoted` and `Table` objects.
- `base.py`: has the base classes of all Pandoc elements. These are `Element` and its subclasses `Block`, `Inline` and `Metadata`.
- `elements.py`: have all the standard Pandoc elements (`Str`, `Para`, `Space`, etc.). Pandoc elements inherit from one of three base classes (`Block`, `Inline` and `Metadata`), which we use to make sure that an elements does not get placed in another element where it's not allowed.
  - Note: there are some elements not present in [pandoc-types](https://github.com/jgm/pandoc-types/blob/master/Text/Pandoc/Definition.hs) that are subclass from `Element` directly. These are `Doc`, `Citation`, `ListItem`, `Definition`, `DefinitionItem`, `TableCell` and `TableRow`. This allow filters to be applied directly to table rows instead of to tables and then looping within each item of the table.
  - `elements.py` also contains the function `from_json`, which is essential in converting JSON elements into Pandoc elements.
- `io.py`: holds all the I/O functions (`load`, `dump`, `run_filters`, and wrappers).
- `tools.py`: contain functions that are useful when writing filters (but not essential). These include `stringify`, `yaml_filter`, `convert_string`, etc.
  - Note: future enhancements to `panflute` should probably go here.
- `autofilter.py`: has the code that allows panflute to be run as an executable script.
  - This allows panflute to be run as a filter (!), in which case it uses the `panflute-...` metadata to conveniently call different filters.


## Documentation

Panflute uses [Sphinx](http://www.sphinx-doc.org/) for its documentation.
To install it, install Python 3.3+ and then run `pip install sphinx` (or see [here](http://www.sphinx-doc.org/en/1.4.8/install.html)).

To build the documentation, navigate to the `/docs` folder and type `make html`. The build files will then be placed in `/docs/build/html`, an can be copied into a [website](scorreia.com/software/panflute/)

The guides are written in [REST](http://www.sphinx-doc.org/en/stable/rest.html) and located in the [/docs/source](https://github.com/sergiocorreia/panflute/tree/master/docs/source) folder.

The API docs are written as comments in the [source code itself](https://github.com/sergiocorreia/panflute/blob/master/panflute/elements.py#L242) (so e.g. [this](http://scorreia.com/software/panflute/code.html) is autogenerated).

### REST guides

- [REST Primer](http://www.sphinx-doc.org/en/stable/rest.html)
- [REST and Sphinx Cheatsheet](http://openalea.gforge.inria.fr/doc/openalea/doc/_build/html/source/sphinx/rest_syntax.html#restructured-text-rest-and-sphinx-cheatsheet)
- [Sphinx commands](https://pythonhosted.org/an_example_pypi_project/sphinx.html)
- [Sphinx domains](http://www.sphinx-doc.org/en/stable/domains.html). This is used to create links to other python packages and to the stdlib (e.g. ``:py:data:`sys.stdin`` `).
