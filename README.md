# Panflute: Pythonic Pandoc Filters

[![Development Status](https://img.shields.io/pypi/status/panflute.svg)](https://pypi.python.org/pypi/panflute/)
[![Build Status](https://github.com/sergiocorreia/panflute/workflows/CI%20Tests/badge.svg)](https://github.com/sergiocorreia/panflute/actions?query=workflow%3A%22CI+Tests%22)
![License](https://img.shields.io/pypi/l/panflute.svg)
[![DOI](https://zenodo.org/badge/55024750.svg)](https://zenodo.org/badge/latestdoi/55024750)

[![GitHub Releases](https://img.shields.io/github/tag/sergiocorreia/panflute.svg?label=github+release)](https://github.com/sergiocorreia/panflute/releases)
[![PyPI version](https://img.shields.io/pypi/v/panflute.svg)](https://pypi.python.org/pypi/panflute/)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/panflute.svg)](https://anaconda.org/conda-forge/panflute)
[![Python version](https://img.shields.io/pypi/pyversions/panflute.svg)](https://pypi.python.org/pypi/panflute/)
[![Supported implementations](https://img.shields.io/pypi/implementation/panflute.svg)](https://pypi.org/project/panflute)

[panflute](http://scorreia.com/software/panflute/) is a Python package that makes creating Pandoc filters fun.

For a detailed user guide, documentation, and installation instructions, see
<http://scorreia.com/software/panflute/>.
For examples that you can use as starting points, check the [examples repo](https://github.com/sergiocorreia/panflute-filters/tree/master/filters), the [sample template](https://raw.githubusercontent.com/sergiocorreia/panflute/master/docs/source/_static/template.py), or [this github search](https://github.com/search?o=desc&q=%22import+panflute%22+OR+%22from+panflute%22+created%3A%3E2016-01-01+language%3APython+extension%3Apy&s=indexed&type=Code&utf8=%E2%9C%93).
If you want to contribute, head [here](/CONTRIBUTING.md).

You might also find useful [this presentation](https://github.com/BPLIM/Workshops/raw/master/BPLIM2019/D2_S1_Sergio_Correia_Markdown.pdf) on how I use markdown+pandoc+panflute to write research papers (at the Banco de Portugal 2019 Workshop on Reproductible Research).


## Installation

### Pip

To manage panflute using pip, open the command line and run

- `pip install panflute` to install
    - `pip install "panflute[extras]"` to include extra dependencies (`yamlloader`)
- `pip install -U panflute` to upgrade
- `pip uninstall panflute` to remove

You need a matching pandoc version for panflute to work flawlessly. See [Supported pandoc versions] for details. Or, use the [Conda] method to install below to have the pandoc version automatically managed for you.

### Conda

To manage panflute with a matching pandoc version, open the command line and run

- `conda install -c conda-forge pandoc 'panflute>=2.0.5'` to install both
    `conda install -c conda-forge pandoc 'panflute>=2.0.5' yamlloader` to include extra dependencies
- `conda update pandoc panflute` to upgrade both
- `conda remove pandoc panflute` to remove both

You may also replace `conda` by `mamba`, which is basically a drop-in replacement of the conda package manager. See [mamba-org/mamba: The Fast Cross-Platform Package Manager](https://github.com/mamba-org/mamba) for details.

### Note on versions

#### Supported Python versions

panflute 1.12 or above dropped support of Python 2. When using Python 3, depending on your setup, you may need to use `pip3`/`python3` explicitly. If you need to use panflute in Python 2, install panflute 1.11.x or below.

Currently supported Python versions: [![Python version](https://img.shields.io/pypi/pyversions/panflute.svg)](https://pypi.python.org/pypi/panflute/). Check `setup.py` for details, which further indicates support of pypy on top of CPython.

#### Supported pandoc versions

pandoc versioning semantics is [MAJOR.MAJOR.MINOR.PATCH](https://pvp.haskell.org) and panflute's is MAJOR.MINOR.PATCH. Below we shows matching versions of pandoc that panflute supports, in descending order. Only major version is shown as long as the minor versions doesn't matter.

<!-- For pandoc API verion, check https://hackage.haskell.org/package/pandoc for pandoc-types, which is the same thing. -->

| panflute version | supported pandoc versions | supported pandoc API versions |
| ---------------- | ------------------------- | ----------------------------- |
| 2.1.3            | 2.11.0.4–2.17.x           | 1.22–1.22.1                   |
| 2.1              | 2.11.0.4—2.14.x           | 1.22                          |
| 2.0              | 2.11.0.4—2.11.x           | 1.22                          |
| not supported    | 2.10                      | 1.21                          |
| 1.12             | 2.7-2.9                   | 1.17.5–1.20                   |

Note: pandoc 2.10 is short lived and 2.11 has minor API changes comparing to that, mainly for fixing its shortcomings. Please avoid using pandoc 2.10.

## Dev Install

After cloning the repo and opening the panflute folder, run

- `python setup.py install` to install the package locally
- `python setup.py develop` to install locally with a symlink so changes are automatically updated

## Contributing

Feel free to submit push requests. For consistency, code should comply with [pep8](https://pypi.python.org/pypi/pep8) (as long as its reasonable), and with the style guides by [@kennethreitz](http://docs.python-guide.org/en/latest/writing/style/) and [google](http://google.github.io/styleguide/pyguide.html). Read more [here](/CONTRIBUTING.md).

## License

BSD3 license (following [`pandocfilters`](https://github.com/jgm/pandocfilters) by @jgm).
