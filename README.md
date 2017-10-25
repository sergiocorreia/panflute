# Panflute: Pythonic Pandoc Filters

[![Python version](https://img.shields.io/pypi/pyversions/panflute.svg)](https://pypi.python.org/pypi/panflute/)
[![PyPI version](https://img.shields.io/pypi/v/panflute.svg)](https://pypi.python.org/pypi/panflute/)
[![Development Status](https://img.shields.io/pypi/status/panflute.svg)](https://pypi.python.org/pypi/panflute/)
[![Build Status](https://travis-ci.org/sergiocorreia/panflute.svg?branch=master)](https://travis-ci.org/sergiocorreia/panflute)

[panflute](http://scorreia.com/software/panflute/) is a Python package that makes creating Pandoc filters fun.

For a detailed user guide, documentation, and installation instructions, see
<http://scorreia.com/software/panflute/>.
For examples that you can use as starting points, check the [examples repo](https://github.com/sergiocorreia/panflute-filters/tree/master/filters), the [sample template](https://raw.githubusercontent.com/sergiocorreia/panflute/master/docs/source/_static/template.py), or [this github search](https://github.com/search?o=desc&q=%22import+panflute%22+OR+%22from+panflute%22+created%3A%3E2016-01-01+language%3APython+extension%3Apy&s=indexed&type=Code&utf8=%E2%9C%93).
If you want to contribute, head [here](/CONTRIBUTING.md).


## Install

To install panflute, open the command line and type:

```bash
pip install panflute
```

Python 2.7+, 3.3+, pypy, and pypy3 are supported.

## Uninstall

```bash
pip uninstall panflute
```

## Dev Install

After cloning the repo and opening the panflute folder:

`python setup.py install`
: installs the package locally

`python setup.py develop`
: installs locally with a symlink so changes are automatically updated

In addition, if you use python2, you need to pasteurize the code before running tests. In this directory, Run

```bash
# install pasteurize if you didn't have it yet
pip2 install -U future
pasteurize -wnj 4 .
```

## Contributing

Feel free to submit push requests. For consistency, code should comply with [pep8](https://pypi.python.org/pypi/pep8) (as long as its reasonable), and with the style guides by [@kennethreitz](http://docs.python-guide.org/en/latest/writing/style/) and [google](http://google.github.io/styleguide/pyguide.html). Read more [here](/CONTRIBUTING.md).

## License

BSD3 license (following  `pandocfilters` by @jgm).

