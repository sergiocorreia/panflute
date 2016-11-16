.. panflute documentation master file, created by
   sphinx-quickstart on Tue Apr 26 22:17:57 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. automodule:: panflute

It is a pythonic alternative to John MacFarlane's
`pandocfilters <https://github.com/jgm/pandocfilters>`_,
from which it is heavily inspired.

To use it, write a function that works on Pandoc elements
and call it through `run_filter <code.html#panflute.io.run_filter>`_::

    from panflute import *

    def increase_header_level(elem, doc):
        if type(elem) == Header:
            if elem.level < 6:
                elem.level += 1
            else:
                return [] #  Delete headers already in level 6

    def main(doc=None):
        return run_filter(increase_header_level, doc=doc)

    if __name__ == "__main__":
        main()


Motivation
====================================

Our goal is to make writing pandoc filters *as simple and clear as possible*. Starting from pandocfilters, we make it pythonic, add error and type checking, and include batteries for common tasks. In more detail:

1. Pythonic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Elements are easier to modify. For instance, to change the level of a
  header, you can do ``header.level += 1`` instead of ``header['c'][0] += 1``.
  To change the identifier, do ``header.identifier = 'spam'`` instead of
  ``header['c'][1][1] = 'spam'``
- Elements are easier to create. Thus, to create a header you can do
  ``Header(Str(The), Space, Str(Title), level=1, identifier=foo)``
  instead of ``Header([1,["foo",[],[]],[{"t":"Str","c":"The"},{"t":"Space","c":[]},{"t":"Str","c":"Title"}])``
- You can navigate across elements. Thus, you can check if ``isinstance(elem.parent, Inline)`` or if ``type(elem.next) == Space``

2. Detects common mistakes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Check that the elements contain the correct types. Trying to create
  `Para('text')` will give you the error "Para() element must contain Inlines
  but received a str()", instead of just failing silently when running the
  filter.

3. Comes with batteries included
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Convert markdown and other formatted strings into python objects or
  other formats, with the
  `convert_text(text, input_format, output_format)` function (which calls
  Pandoc internally)
- Use code blocks to hold YAML options and other data (such as CSV) with
  `yaml_filter(element, doc, tag, function)`.
- Called external programs to fetch results with `shell()`.
- Modifying the entire document (e.g. moving all the figures and tables to the
  back of a PDF) is easy, thanks to the `prepare` and `finalize`
  options of `run_filter`, and to the `replace_keyword` function
- Convenience elements such as `TableRow` and `TableCell` allow for easier
  filters.
- Panflute can be run as a filter itself, in which case it will run all
  filters listed in the metadata field `pandoc-filters`.

Examples of panflute filters
====================================

Ports of existing pandocfilter modules are in the `github repo <https://github.com/sergiocorreia/panflute/tree/master/examples/panflute>`_; additional and more advanced examples are in a `separate repository <https://github.com/sergiocorreia/panflute-filters>`_.

Also, a comprehensive list of filters and other Pandoc extras should be
available `here <https://github.com/pandoc-extras/>`_ in the future.

Alternative: filters based on pandocfilters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- For a guide to pandocfilters, see the
  `repository <https://github.com/jgm/pandocfilters>`_
  and the `tutorial <http://pandoc.org/scripting.html>`_.
- The repo includes `sample filters
  <https://github.com/jgm/pandocfilters/tree/master/examples>`_.
- The wiki lists useful `third party filters
  <https://github.com/jgm/pandoc/wiki/Pandoc-Filters>`_.

Contents:
====================================

.. toctree::
   :maxdepth: 3

   guide
   install
   code
   about


Indices and tables
====================================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

