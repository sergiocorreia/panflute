User guide
==========


A Simple filter
***************

Suppose we want to create a filter that sets all headers to level 1. For this, write this python script:

.. literalinclude:: _static/header-level-1.py

.. note:: a more complete template is `located here <https://github.com/sergiocorreia/panflute/tree/master/docs/source/_static/template.py>`_

.. tip:: ``import panflute as pf`` (as in the template) makes a filter start
   faster than ``from panflute import *``: since panflute 3.0, the first one
   does not import the modules used by panflute's command line tools (such as
   ``click``), while the star import still imports all of them. This saves a few
   tens of milliseconds every time pandoc runs the filter.

More complex filters
********************

We might want filters that replace an element instead of just modifying it.
For instance, suppose we want to replace all emphasized text with striked
out text:

.. literalinclude:: _static/emph2strikeout.py

Or if we want to remove all tables:

.. literalinclude:: _static/remove-tables.py


Globals and backmatter
**********************

Suppose we want to add a table of contents based on all headers, or move all tables to a specific location in the document. This requires tracking global
variables (which can be stored as attributes of ``doc``).

To add a table of contents at the beginning:

.. literalinclude:: _static/toc.py

To move all tables to the place where the string *$tables* is:

.. literalinclude:: _static/move-tables.py


Using the included batteries
****************************

There are several functions and methods that make your life easier, such as
the `replace_keyword <code.html#panflute.base.Element.replace_keyword>`_
method shown above.

Other useful functions include
`convert_text <code.html#panflute.tools.convert_text>`_
(to load and parse markdown or other formatted text) and
`stringify <code.html#panflute.tools.stringify>`_ 
(to extract the underlying text from an element and its children).
For metadata, you can use the `doc.get_metadata <code.html#panflute.elements.Doc.get_metadata>`_ attribute to extract user--specified options (booleans, strings, etc.)

For instance, you can combine these functions to allow for include directives (so you can include and parse markdown files from other files).

.. literalinclude:: _static/include.py


YAML code blocks
****************

A YAML filter is a filter that parses fenced code blocks
that contain YAML metadata. For instance:

.. code-block:: none

    Some text

    ~~~ csv
    title: Some Title
    has-header: True
    ---
    Col1, Col2, Col3
    1, 2, 3
    10, 20, 30
    ~~~

    More text

Note that fenced code blocks use three or more
`tildes <https://pandoc.org/MANUAL.html#extension-fenced_code_blocks>`_
or
`backticks <https://pandoc.org/MANUAL.html#extension-backtick_code_blocks>`_
as separators.
Within a code block, use `three hyphens or three dots <https://pandoc.org/MANUAL.html#extension-yaml_metadata_block>`_
to separate the YAML options from the rest of the block.


As an example, we will design a filter that will be applied to
all code blocks with the *csv* class, like the one shown above.
To avoid boilerplate code (such as parsing the YAML part), we use the
useful `yaml_filter <code.html#panflute.tools.yaml_filter>`_ function:

.. literalinclude:: _static/csv-tables.py

.. note:: a more complete template is `here <https://github.com/sergiocorreia/panflute/tree/master/docs/source/_static/fenced-template.py>`_ , a fully developed filter for CSVs is `also available <https://github.com/ickc/pantable>`_.

.. note:: `yaml_filter` now allows a `strict_yaml=True` option, which allows multiple YAML blocks, but with the caveat that all YAML blocks must start with `---` and end with `---` or `...`.
   In this mode, a YAML block that cannot be parsed, or that is not a mapping of ``key: value`` pairs, is reported on stderr and the code block is left unchanged.


Calling external programs
******************************

We might also want to embed results from other programs.

One option is to do so through Python's internals.
For instance, we can use fetch data from wikipedia and show it on the document.
Thus, the following script will replace links like these: ``[Pandoc](wiki://)``
With this "Pandoc is a free and open-source software document converter...".

.. literalinclude:: _static/wiki.py

Alternatively, we might want to run other programs through the shell.
For this, explore the `shell <code.html#panflute.tools.shell>`_
function.

.. _navigation:

Navigating through the document tree
************************************

You might wish to apply a filter that depends on the parent or sibling objects of an element. For instance, Modify the first row (`TableRow`) of a table, or all the `Str` items nested within a header.

For this, every element has a `.parent` attribute (and the related `.next`, `.prev`, `.ancestor(#)`, `.index_in_parent`, `.offset(#)` attributes; `.index` is an alias of `.index_in_parent`, except on a `MetaList`, where `.index()` is the list method).

For example, the code below will emphasize all text in the last row of every table:

.. literalinclude:: _static/emph-last-row.py

These attributes are:

- ``.parent``: the element that contains this one (``None`` for the
  :class:`.Doc`, and for an element that is not part of another one).
- ``.location``: ``None`` when the element is in the ``.content`` of its
  parent; otherwise, the name of the attribute of the parent that holds it,
  such as ``'caption'`` or ``'head'`` for a table, or ``'citations'``
  for a :class:`.Cite`.
- ``.index_in_parent``: the index of the element within the list that
  ``.location`` names, so that
  ``elem.container[elem.index_in_parent] is elem``. A parent can hold
  several lists (the ``.term`` and ``.definitions`` of a
  :class:`.DefinitionItem`, for instance), and the index counts only within
  the element's own list. ``None`` when no list holds the element: the
  :class:`.Doc`, an element without a parent, the ``.caption`` of a table,
  or a value of a :class:`.MetaMap`. ``.index`` is the older name of this
  attribute, and still works on every element except :class:`.MetaList`
  (see below).
- ``.next``, ``.prev`` and ``.offset(n)``: the sibling elements in the same
  list (or ``None``), and ``.ancestor(n)``: the parent of the parent, etc.
- ``.container``: the list (or dict) that holds the element, and ``.doc``:
  the root :class:`.Doc`, if there is one.

.. code-block:: python

    >>> para = Para(Str('a'), Space(), Str('b'))
    >>> b = para.content[2]
    >>> b.parent is para, b.index_in_parent, b.prev, b.offset(-2)
    (True, 2, Space, Str(a))

These attributes are set as soon as an element is added to another one
(when building it, or with ``append()``, ``insert()``, ``elem.content[i] = ...``,
``elem.content = [...]``, etc.), and the containers keep ``.index_in_parent``
up to date when elements are inserted or deleted. An element that is removed from its parent
keeps its old ``.parent`` and ``.index_in_parent``.

.. note:: :class:`.MetaList` is a list-like object, so ``metalist.index(value)``
   is the standard list method (the position of ``value`` in the list), as is
   ``metalist.remove(value)``. The index of a :class:`.MetaList` in its own
   container is ``metalist.index_in_parent``. (In panflute 2.x,
   ``metalist.index`` was that index.)

Lists of elements and slices
****************************

The ``.content`` of an element (and other lists of elements, such as the
``.citations`` of a :class:`.Cite`) is a :class:`.ListContainer`: a
list-like object that only accepts elements of the right type, and that
sets their ``.parent`` and ``.index_in_parent``. It supports the usual list
operations (``append``, ``insert``, ``del``, ``elem.content[i:j] = [...]``, etc.).

A slice such as ``para.content[1:3]`` is a new container that holds the same
elements; changing the slice does not change ``para.content``, and reading
it does not change the ``.parent`` or ``.index_in_parent`` of the elements. A slice is an
instance of a (private) subclass of :class:`.ListContainer`, so check its type
with ``isinstance(s, ListContainer)``, or use ``list(s)`` to get a plain list.

Raw formats
***********

:class:`.RawBlock` and :class:`.RawInline` hold text in a given output format,
which pandoc copies as-is into documents of that format. Any format name is
accepted, as in pandoc, for instance ``'html'``, ``'latex'``, ``'typst'``, or
``'comment'`` (which pandoc drops from every output), or the name of a custom writer:

.. code-block:: python

    def action(elem, doc):
        if isinstance(elem, RawBlock) and elem.format == 'comment':
            return []  # Delete comments, whatever the output format

    page_break = RawBlock('#pagebreak()', format='typst')

(Before panflute 3.0, only a fixed list of formats was accepted, so documents
with other raw formats could not be loaded.)


.. _running-filters-automatically:

Running filters automatically
******************************

If you run panflute as a filter (``pandoc ... -F panflute``), then panflute will run all filters specified in the metadata field ``panflute-filters``. This is faster and more convenient than typing the precise list and order of filters used every time the document is run.

You can also specify the location of the filters with the ``panflute-path`` field, which will take precedence over Pandoc's search `locations <https://pandoc.org/MANUAL.html#reader-options>`_ (``.``, ``$datadir/filters``, and ``$path``).

Example:

.. literalinclude:: _static/autofilters.md

For this to work, the filters need to have a very specific
structure, with a `main()` function of the following form:

.. literalinclude:: _static/template.py

.. note:: To be able to run filters automatically, the main function needs to be exactly as shown, with an optional argument ``doc``, that gets passed to ``run_filter``, and which is ``return`` ed back.

.. note:: You can add ``panflute-verbose: true`` to the metadata to display debugging information, including the folders searched and the filters executed.

Command line tools
******************

Installing panflute also installs two command line programs:

- ``panflute`` is the filter used above (``pandoc -F panflute``): it runs the
  filters listed in the metadata. ``panflute --help`` describes it, and
  ``panflute --version`` prints panflute's version.
- ``panfl`` can do the same (``pandoc -F panfl``), and can also run filters
  given on the command line, in a pipeline of pandoc commands. With the
  ``-t``/``--to`` option it runs several filters at once, searching for them
  in the directories given with ``-d`` (``--dir``), in pandoc's data directory
  (``--data-dir``), and in Python's ``sys.path`` (unless ``--no-sys-path``):

  .. code-block:: none

      pandoc example.md -t json | panfl foo.bar -t markdown | pandoc -f json

  Run ``panfl --help`` for all the options.


.. _type-hints:

Type hints
**********

Panflute comes with type hints, so a type checker (mypy, pyright, ...) or
an IDE can check your filters and complete the attributes of each element.
Annotate an action like this:

.. code-block:: python

    import panflute as pf

    def action(elem: pf.Element, doc: pf.Doc) -> pf.Element | list[pf.Element] | None:
        if isinstance(elem, pf.Str):
            return pf.Str(elem.text.upper())  # replace the element
        if isinstance(elem, pf.Emph):
            return []  # delete the element
        return None  # keep the element

    def prepare(doc: pf.Doc) -> None:
        doc.count = 0  # filters can store their own attributes in the Doc

    def main(doc: pf.Doc | None = None) -> pf.Doc | None:
        return pf.run_filter(action, prepare=prepare, doc=doc)

``isinstance()`` checks narrow the type of ``elem``, so that e.g. ``elem.text``
is known to be a ``str`` after ``isinstance(elem, pf.Str)``.
Arguments that only take a few values have ``Literal`` types (for instance
``Quoted(quote_type='SingleQuote')`` or ``OrderedList(style='LowerRoman')``),
so a typo is reported by the type checker.

The types are simplified in a few places, deliberately:

- The ``doc`` passed to an action is typed :class:`.Doc`, although it is
  ``None`` when ``walk()`` is called on an element that is not part of a
  document.
- ``.identifier``, ``.classes`` and ``.attributes`` are declared on every
  element, although only the elements that have attributes (such as
  :class:`.Div`, :class:`.Header` or :class:`.Code`) have them.
- Panflute accepts an element class where an element is expected
  (``Para(Str('a'), Space)`` instead of ``Para(Str('a'), Space())``), but the
  type hints only accept instances.

