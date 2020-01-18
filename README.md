# Panflute: Pythonic Pandoc Filters

[![Python version](https://img.shields.io/pypi/pyversions/panflute.svg)](https://pypi.python.org/pypi/panflute/)
[![PyPI version](https://img.shields.io/pypi/v/panflute.svg)](https://pypi.python.org/pypi/panflute/)
[![Development Status](https://img.shields.io/pypi/status/panflute.svg)](https://pypi.python.org/pypi/panflute/)
[![Build Status](https://github.com/sergiocorreia/panflute/workflows/CI%20Tests/badge.svg)](https://github.com/sergiocorreia/panflute/actions?query=workflow%3A%22CI+Tests%22)

[panflute](http://scorreia.com/software/panflute/) is a Python package that makes creating Pandoc filters fun.

For a detailed user guide, documentation, and installation instructions, see
<http://scorreia.com/software/panflute/>.
For examples that you can use as starting points, check the [examples repo](https://github.com/sergiocorreia/panflute-filters/tree/master/filters), the [sample template](https://raw.githubusercontent.com/sergiocorreia/panflute/master/docs/source/_static/template.py), or [this github search](https://github.com/search?o=desc&q=%22import+panflute%22+OR+%22from+panflute%22+created%3A%3E2016-01-01+language%3APython+extension%3Apy&s=indexed&type=Code&utf8=%E2%9C%93).
If you want to contribute, head [here](/CONTRIBUTING.md).

You might also find useful [this presentation](https://github.com/BPLIM/Workshops/raw/master/BPLIM2019/D2_S1_Sergio_Correia_Markdown.pdf) on how I use markdown+pandoc+panflute to write research papers (at the Banco de Portugal 2019 Workshop on Reproductible Research).


## Install

To install panflute, open the command line and type:

```bash
pip install panflute
```

Python 3.6+ and PyPy3 are supported (Python 2.7 and Python 3.3-3.5 were supported up to version 1.11.4).

## Uninstall

```bash
pip uninstall panflute
```

## Dev Install

After cloning the repo and opening the panflute folder:

`python setup.py install`: installs the package locally

`python setup.py develop`: installs locally with a symlink so changes are automatically updated


## Contributing

Feel free to submit push requests. For consistency, code should comply with [pep8](https://pypi.python.org/pypi/pep8) (as long as its reasonable), and with the style guides by [@kennethreitz](http://docs.python-guide.org/en/latest/writing/style/) and [google](http://google.github.io/styleguide/pyguide.html). Read more [here](/CONTRIBUTING.md).

## License

BSD3 license (following  `pandocfilters` by @jgm).

