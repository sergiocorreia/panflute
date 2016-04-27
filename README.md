# Panflute: Pythonic Pandoc Filters

`panflute` is a Python package that makes creating Pandoc filters fun. It is heavily inspired by [`pandocfilters`](https://github.com/jgm/pandocfilters), with additional goals:

- Pythonic:
  - Elements are easier to modify. For instance, to change the level of a header, you can do `header.level += 1` instead of `header['c'][0] += 1`. To change the identifier, do `header.identifier = 'spam'` instead of `header['c'][1][1] = 'spam'`
  - Elements are easier to create. Thus, to create a header you can do `Header(Str(The), Space, Str(Title), level=1, identifier=foo)`
    instead of `Header([1,["foo",[],[]],[{"t":"Str","c":"The"},{"t":"Space","c":[]},{"t":"Str","c":"Title"}])`
- Detect common mistakes:
  - Check that the elements contain the correct types. Trying to create `Para('text')` will give you the error "Para() element must contain Inlines but received a str()", instead of just failing silently when running the filter.
- Batteries included:
  - Convert markdown strings into python objects or other formats, with the `convert_markdown(text, format)` function (which calls Pandoc internally)
  - Use code blocks to hold YAML options and other data (such as CSV) with `yaml_filter(element, doc, tag, function)`.
  - Called external programs to fetch results with `shell()`.
  - Modifying the entire document (e.g. moving all the figures and tables to the back of a PDF) are easy to use, thanks to the `prepare` and `finalize` options of `toJSONFilter`, and to the `replace_keyword` function
- Better documentation (work in progress):
  - Calling `help(Para)` gives more useful information (as well as autocompletion)

# Example

This filter converts all headers to a lower level, and deletes headers of level 6:

``` python
from panflute import *

def increase_header_level(elem, doc):
	if type(elem)==Header:
		if elem.level < 6:
			elem.level += 1
		else:
			return []

if __name__ == "__main__":
    toJSONFilter(increase_header_level)
```

More advanced example can be found in the [examples/panflute folder](/examples/panflute) and in the [panflute-filters project](https://github.com/sergiocorreia/panflute-filters)

# Documentation

Currently, documentation is either in the code, or in the [documentation](/documentation.md) page ([html](/documentation.html), [pdf](/documentation.pdf)). It is being improved gradually (requests are more than welcome!).

# About Pandoc Filters

- For a guide to pandocfilters, see the [repository](https://github.com/jgm/pandocfilters)
and the [tutorial](http://pandoc.org/scripting.html).
- The repo includes [sample filters](https://github.com/jgm/pandocfilters/tree/master/examples).
- The wiki lists useful [third party filters](https://github.com/jgm/pandoc/wiki/Pandoc-Filters).

# Install

Run:

```
pip install git+git://github.com/sergiocorreia/pandocfilters_extended.git
```

(Windows note: open `cmd` as administrator)

# Dev Install

`python setup.py install`
: installs the package locally

`python setup.py develop`
: installs locally with a symlink so changes are automatically updated

# Contributing

Feel free to submit push requests. For consistency, code should comply with [pep8](https://pypi.python.org/pypi/pep8) (as long as its reasonable), and with the style guides by [@kennethreitz](http://docs.python-guide.org/en/latest/writing/style/) and [google](http://google.github.io/styleguide/pyguide.html).

# License

BSD3 license (following  `pandocfilter` by @jgm)

